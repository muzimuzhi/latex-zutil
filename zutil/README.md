# Z's utilities, experimental LaTeX macros

- `zutil` package

  - base package
    - `\zutil_set:n {⟨key-value list⟩}`
    - `\zutil_load_module:n {⟨module⟩}`
      - for now, all modules are loaded automatically

  - `l3extras` module
    - additions to standard `l3kernel` functions
    - `l3prg` extras
      - `\zutil_cs_if_defined:N(TF) ⟨cs⟩ {⟨true code⟩} {⟨false code⟩}`
        - variant `c`
        - similar to `\cs_if_exist:NTF` but treats `\relax` as defined
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

  - `debug` module
    - adding debugging info to log
    - main functions
      - `\zutil_debug:nn {⟨debug options⟩} {⟨debug text⟩}`
        - adds debug info; `⟨debug text⟩` is used as string
        - example: `\zutil_debug:nn {label=a} {\ERROR}` adds `! debug [a] >>\ERROR <<` to log, using default settings
      - `\zutil_debug:nN {⟨debug options⟩} ⟨debug token⟩`
        - adds debug info; uses meaning of `⟨debug token⟩` as debug text
        - variant `eN`, `nc`, `ec`
      - `\zutil_debug:n {⟨debug text⟩}`
        - variant `e`
      - `\zutil_debug:N {⟨debug text⟩}`
        - variant `c`
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
        - `reset-labels`: clear all labels
        - `reset-label`: alias of `reset-labels`
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

  - `softerror` module
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
      - variant `nnnee`, `nneee`
    - `\zutil_msg_softerror:nnnn`
      - variant `nnVV`, `nnVn`, `nnnV`, `nnne`, `nnee`
    - `\zutil_msg_softerror:nnn`
      - variant `nnV`, `nne`
