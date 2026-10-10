# Static metrics using Ruby's own parser, not line-based guesses of cyclomatic complexity.
require 'ripper'
require 'json'
require 'digest'

DECISIONS = %i[if elsif unless if_mod unless_mod while until while_mod until_mod for ifop when rescue].freeze

def walk(node, &block)
  return unless node.is_a?(Array)
  yield node
  node.each { |child| walk(child, &block) if child.is_a?(Array) }
end

def methods(ast)
  result = []
  walk(ast) do |node|
    next unless %i[def defs].include?(node[0])
    token = node[0] == :def ? node[1] : node[3]
    body = node[-1]
    decisions = 0
    walk(body) do |child|
      decisions += 1 if DECISIONS.include?(child[0])
      decisions += 1 if child[0] == :binary && %i[&& || and or].include?(child[2])
    end
    result << {name: token[1], line: token[2][0], cc: 1 + decisions}
  end
  result
end

root = File.expand_path(ARGV.fetch(0))
files = Dir[File.join(root, 'app/**/*.rb')].sort
owned = files.flat_map do |path|
  File.read(path).scan(/\b(?:class|module)\s+([A-Z][A-Za-z0-9_:]*)/).flatten.map { |name| name.split('::').last }
end.uniq
rows = files.map do |path|
  source = File.read(path)
  ast = Ripper.sexp(source)
  raise "Unparseable Ruby: #{path}" unless ast
  declarations = source.scan(/\b(?:class|module)\s+([A-Z][A-Za-z0-9_:]*)/).flatten.map { |n| n.split('::').last }
  # Explicit application-owned constant references; excludes declarations, strings,
  # dynamic Rails associations, framework/gem constants and inferred call graph edges.
  constants = Ripper.lex(source).select { |token| token[1] == :on_const }.map { |token| token[2] }.uniq
  deps = (constants & owned) - declarations
  ms = methods(ast)
  {path: path.delete_prefix(root + '/').tr('\\', '/'), sha256: Digest::SHA256.hexdigest(File.binread(path)),
   sloc: source.lines.count { |line| !line.strip.empty? && !line.lstrip.start_with?('#') },
   method_count: ms.size, sum_method_cc: ms.sum { |m| m[:cc] }, max_method_cc: ms.map { |m| m[:cc] }.max || 0,
   explicit_app_dependencies: deps.sort, methods: ms}
end
puts JSON.pretty_generate(rows)
