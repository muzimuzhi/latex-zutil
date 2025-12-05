# `zutil` - experimental LaTeX utility macros

## base package
- package option(s)
  - `presets[=none|util|test|debug|all]` (default `util`)
    - `none`: load no modules
    - `util`: load `l3extras` module
    - `test`: `util` presets + `softerror` module
    - `debug`: `util` presets + `debug` and `unravel` modules
    - `all`: load all modules
- `\zutil_set:n {⟨key-value list⟩}`
- `\zutil_load_module:n {⟨module⟩}`
  - load a single module

## `l3extras` module
- additions to the `l3kernel`
- `l3basics` extras
  - `\zutil_cs_if_function:NTF ⟨cs⟩ {⟨true code⟩} {⟨false code⟩}`\
    `\zutil_cs_if_function_p:N ⟨cs⟩`
    - checks if the csname of `⟨cs⟩` contains colon `:`
  - `\zutil_cs_function_name:N ⟨cs⟩`\
    `\zutil_cs_function_signature:N ⟨cs⟩`
    - expands to name or signature of an expl3 function (in string); if colon not found then leaves `\q_no_value`. The result is returned within `\exp_not:n`. See also `\cs_split_function:N`.
  - `\zutil_cs_base_function:N ⟨cs⟩`
    - expands to base-form of an expl3 function (in `⟨token⟩`); if colon not found then leaves `\q_no_value`. The result is returned within `\exp_not:n`.
- `l3prg` extras
  - `\zutil_cs_if_defined:NTF ⟨cs⟩ {⟨true code⟩} {⟨false code⟩}`\
    `\zutil_cs_if_defined_p:N ⟨cs⟩`
    - variant `c` (hand-tuned, no `\relax` issue)
    - similar to `\cs_if_exist:NTF` but treats `\relax` as defined
  - `\zutil_exp_args_safe:Nc ⟨cs⟩ ⟨csname⟩`
    - safe `c`-type expansion which doesn't define the `\⟨csname⟩` to `\relax` if it's undefined before
    - expands to `\group_begin: \group_end: ⟨cs⟩ \⟨csname⟩`
- `l3expan` extras
  - `\zutil_cs_generate_variant:N ⟨cs variant⟩`
    - similar to `\cs_generate_variant:Nn` but accepts the variant function name as argument
    - example: `\zutil_cs_generate_variant:N \zutil_set:V`
  - `\zutil_cs_generate_variant:n {⟨cs variants list⟩}`
    - example: `\zutil_cs_generate_variant:n { \zutil_set:v, \zutil_set:e }`
- `l3tl` extras
  - `\zutil_prg_new_conditional_tl_if_in:Nnn \⟨name⟩:⟨arg spec⟩ {⟨test token list⟩} {⟨conditions⟩}`
    - variants `Non`, `NVn`, `Nen`
    - works like `\prg_new_conditional:N(p)nn` but specifically creates expandable conditional to test if `⟨test token list⟩` is in an token list
    - example: `\zutil_prg_new_conditional_tl_if_in:Nnn \zutil_if_colon_in:n { : } { TF }` which defines expandable `\zutil_if_colon_in:nTF` with usage `\zutil_if_colon_in:nTF {⟨token list⟩} {⟨true code⟩} {⟨false code⟩}`
- `l3seq` extras
  - `\zutil_seq_set_split_keep_braces:Nnn ⟨seq var⟩ {⟨delimiter⟩} {⟨token list⟩}`
    - `gset` version `\zutil_seq_gset_split_keep_braces:Nnn`
    - variants `NnV`
    - like `\seq_set_split(_keep_spaces):Nnn` but only trims surrounding spaces only, any outer braces are retained. Errors on empty `⟨delimiter⟩`.

## `l3patch` module
- additions to the `l3kernel`, involving patches
- `l3msg` extras
  - `\zutil_msg_space_safe_on: ... \zutil_msg_space_safe_off:`
    - `\msg_new:nnn(n)` and `\msg_set:nnn(n)` used in between them will respect space characters and trim spaces from both sides of all the arguments. Nestable. (If used nested, only the outer-most pair takes effect.)
    - restriction: to ensure the catcode change works and only works locally, `\zutil_msg_space_safe_(on|off):` should be used on their own line(s).
    - example:
      ```tex
      \zutil_msg_space_safe_on:
      \msg_new:nnn {⟨module⟩} {⟨message⟩} {⟨text⟩}
      ...
      \zutil_msg_space_safe_off:
      ```
  - `\zutil_msg_suspend_debug: ... \zutil_msg_resume_debug:`
    - suspend and resume debugging (the same as `\debug_suspend:` and `\debug_resume:`) inside functions that issue messages (`\msg_<type>:nn...`), to make msg-based tests quicker. Nestable.

## `debug` module
- write debugging info to log; depends on the `l3extras` module
- main functions
  - `\zutil_debug:nn {⟨debug options⟩} {⟨debug text⟩}`
    - adds debug info; `⟨debug text⟩` is used as string
    - variants `ne`, `en`, `ee`
    - example: `\zutil_debug:nn {label=a} {\ERROR}` adds `! debug [a] >>\ERROR <<` to log, using default settings
  - `\zutil_debug:nN {⟨debug options⟩} ⟨debug token⟩`
    - adds debug info; uses meaning of `⟨debug token⟩` as debug text
    - variants `nc` (hand-tuned, no `\relax` issue), `eN`, `ec`
  - `\zutil_debug:n {⟨debug text⟩}`
    - variant `e`
  - `\zutil_debug:N {⟨debug text⟩}`
    - variant `c` (hand-tuned, no `\relax` issue)
  - <sub>\* Unless marked with "hand-tuned", all variants in this function family are generated with `\zutil_debug_generate_variant:Nn`, in order to add appropriate collectors used by decorator functions (see below).</sub>
- LaTeX2e interfaces
  - `\ZutilDebug [⟨debug options 1⟩] {⟨debug text⟩} [⟨debug options 2⟩]`
    - equivalent to `\zutil_debug:nn {⟨debug options 1⟩,⟨debug options 2⟩} {⟨debug text⟩}`
  - `\ZutilDebugCmd [⟨debug options 1⟩] {⟨debug token⟩} [⟨debug options 2⟩]`
    - equivalent to `\zutil_debug:nN {⟨debug options 1⟩, ⟨debug options 2⟩} ⟨debug token⟩`
- the option-setting function
  - `\zutil_debug_set:n {⟨debug options⟩}`
- debug options
  - label family
    - `label=⟨label⟩`: converts  to string and adds the result as label
    - `e=⟨label⟩`: fully expands `⟨label⟩` and adds the result as label
    - `reset-labels`: clear all labels; alias `reset-label`; available to `\zutil_debug_set:n` only
    - unknown keys are treated as passed to `label`
  - level family
    - `+`: increases indent level by 1
    - `-`: decreases indent level by 1
  - misc
    - `if=⟨bool expr⟩`: only add debugging info if `⟨bool expr⟩` evaluates to true
  - `tabularray` integration
    - `tblr`: short for `label={⟨row⟩, ⟨column⟩}`
- decorator functions
  - `\zutil_debug_if:n {⟨bool expr⟩} \zutil_debug:...`
    - used as a easy-to-comment decorator/prefix of `\zutil_debug:...`; an alternative way of setting `if` option
  - `\zutil_debug_safe_if:n {⟨bool expr⟩}`
    - similar to `\zutil_debug_if:n` and safe in expansion-only circumtances
- [unstable] helper function
  - `\zutil_debug_generate_variant:Nn`

## `softerror` module
- new `l3msg` message level `softerror`
  - like `error`, it uses both `⟨text⟩` and `⟨more text⟩` of a message
  - like `warning`, it doesn't interrupt processing nor prompting for user input, thus produces portable and compact messages
  - it's most suitable for log-based tests
- full example
  ```tex
  \msg_new:nnnn { mypkg } { msg } { text } { more text }
  \zutil_msg_softerror:nn { mypkg } { msg }
  ```
  generates
  ```
  ! Package mypkg Error: text
  (mypkg)                more text
  ```
- `\zutil_msg_softerror:nnnnnn`
  - variant `nneeee`
- `\zutil_msg_softerror:nnnnn`
  - variants `nnnee`, `nneee`
- `\zutil_msg_softerror:nnnn`
  - variants `nnVV`, `nnVn`, `nnnV`, `nnne`, `nnee`
- `\zutil_msg_softerror:nnn`
  - variants `nnV`, `nne`

## `unravel` module
- provides thin wrapper for `unravel` package
- `\beginunravel[⟨options⟩]⟨code⟩\endunravel`
  - equivalent to using `\unravel[⟨options⟩]{⟨code⟩}`

## `zutil-regression-test.tex` file
- `l3build` `regression-test.tex` extended
- new features
  - removed test numbering
  - log number of errors and passed checks at the end of a test and the entire test file
    - errors raised through `\errmessage` are all counted
    - checks are stepped by the `\PASSED` new expandable command
- new commands
  - `\PASSED`
  - `\FAILED` (undefined, can be used as `\ERROR`)
