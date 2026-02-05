-- Toggle selected explcheck configs
if arg[1] == nil then
  print("Usage: texlua explcheck-toggle-configs.lua [enable|disable]")
  os.exit(1)
end

local path = ".explcheckrc"
local toggled_configs = {
  "stop_after",
  "stop_early_when_confused",
}

local match_prefix, replace_prefix

if arg[1] == "enable" then
  match_prefix = "^# "
  replace_prefix = ""
elseif arg[1] == "disable" then
  match_prefix = "^"
  replace_prefix = "# "
end

local content = io.open(path, "r"):read("*a")
local new_content = ""

for line in content:gmatch("([^\n]*)\n") do
  for _, config in ipairs(toggled_configs) do
    if line:match(match_prefix .. config .. "%s*=") then
      line = line:gsub(match_prefix .. "(" .. config .. "%s*=)", replace_prefix .. "%1")
      break
    end
  end
  new_content = new_content .. line .. "\n"
end

-- print(new_content)

io.open(path, "w"):write(new_content):close()
