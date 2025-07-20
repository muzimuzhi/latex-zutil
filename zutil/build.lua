module = "zutil"


maindir         = ".."

sourcefiles     = { "*.sty", "*.tex" }
installfiles    = { "*.sty", "*.tex" }

checkengines    = { "pdftex", "xetex", "luatex" }
stdengine       = "pdftex"
checksuppfiles  = { "zutil-regression-test.cfg" }

-- show message of expandable errors as full as possible
-- these are the maximum values accepted by the TeX Live, see texmf.cnf
--
-- setting them in the top-level `build.lua` file doesn't work, because
-- running `l3build` in `./zutil` won't even load the top-level `build.lua`.
errorline       = 254
halferrorline   = 239

-- custom log normalization
local open             = io.open
local close            = io.close
local write            = io.write
local output           = io.output

local gsub             = string.gsub
local gmatch           = string.gmatch
local match            = string.match

local function rewrite(source,result,processor,...)
  -- overwrite result file
  local file = assert(open(result,"rb"))
  local content = gsub(file:read("a") .. "\n","\r\n","\n")
  close(file)
  local new_content
  new_content = processor(content,...)
  local newfile = assert(open(result,"w"))
  output(newfile)
  write(new_content)
  close(newfile)
end

local function normalize_log_extra(content, engine, errlevels)
  local function normalize(line)
    line = gsub(line, "^Type  H <return>  for immediate help.*", "")
    line = gsub(line, "^For immediate help type H <return>.*", "")
    line = gsub(line, "^Type <return> to continue.*", "")
    line = gsub(line, "^ %->\\errmessage  .*", " ...")
    line = gsub(line, "^ %->\\tex_errmessage:D  .*", " ...")
    line = gsub(line, "^See the .* package documentation for explanation%.$", "")
    line = gsub(line, "^See the .* class documentation for explanation%.$", "")
    line = gsub(line, "^See the LaTeX manual or LaTeX Companion for explanation%.$", "")

    -- if match(line, "\\errmessage") then
    --   print("[before] " .. line)
    --   local after = gsub(line, "^ %-> \\errmessage", " ...")
    --   print("[after] " .. after)
    -- end
    -- line = gsub(line, "^See the test package documentation for explanation.$", "")
    -- line = gsub(line, "^ %->\\errmessage.*", " ...")
    -- line = gsub(line, "^ %->\\tex_errmessage:D.*", " ...")
    return line
  end

  local skipping_lines = 0
  local new_content = ""
  for line in gmatch(content, "([^\n]*)\n") do
    -- if skipping_lines > 0 then
    --   line = ""
    --   skipping_lines = skipping_lines - 1
    --   goto continue
    -- end
    line = normalize(line)
    -- ::continue::
    if line ~= "" then
      new_content = new_content .. line .. "\n"
    end
  end
  return new_content
end

local rewrite_log_old = rewrite_log
function rewrite_log(source, result, engine, errlevels)
  rewrite_log_old(source, result, engine, errlevels)
  rewrite(source, result, normalize_log_extra, engine, errlevels)
end
