# Experimental LaTeX utility macros

- `zutil` package

  - base package
    - `\zutil_set:n {⟨key-value list⟩}`
    - `\zutil_load_module:n {⟨module⟩}`
      - for now, all modules are loaded automatically

  - `l3extras` module
    - `l3prg` extras
      - `\zutil_cs_if_defined:N(TF) ⟨cs⟩ {⟨true code⟩} {⟨false code⟩}`
        - variant `c`
        - similar to `\cs_if_exist:NTF` but treats `\relax` as defined
    - `l3expan` extras
      - `\zutil_cs_ensure_variant:N ⟨cs variant⟩`
        - similar to `\cs_generate_variant:Nn` but accepts the variant function name as argument
        - example: `\zutil_cs_ensure_variant:N \zutil_set:V`
      - `\zutil_cs_ensure_variant:n {⟨cs variants list⟩}`
        - example: `\zutil_cs_ensure_variant:n { \zutil_set:v, \zutil_set:e }`
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
