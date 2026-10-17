# Issues in tax_calculator.py

| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| New-regime tax uses one flat rate on all income | Logic bug (no tool flags it) | 18-41 | `taxable * slabRate(taxable)` taxes the whole income at the top slab's rate instead of each slice at its own rate. Salary 18,00,000 gave 358,800; correct is 150,800. | Added `_progressive_tax()` with `NEW_SLABS`, taxing each slice at its own rate. |
| Rebate boundary wrong and cess charged after rebate | Logic bug | 38-41 | `taxable < REBATE_LIMIT_NEW` should be `<=`, so salary 12,75,000 (taxable exactly 12,00,000) paid 124,800 instead of 0. Cess was computed before the rebate, so it survived a zeroed tax. | Use `<=`, apply rebate first, then cess on the net tax. Added marginal relief just above the limit. |
| `betterRegime` comparison inverted | Logic bug | 66 | Returned "new" when `newTax > oldTax`, so it picked the more expensive regime. | Return "new" when `new_tax <= old_tax`. |
| Age-80 boundary wrong | Logic bug | 44-47 | `age > 80` excludes exactly 80, so an 80-year-old got 2,50,000 instead of 5,00,000 exemption. | `age >= 80`, then `age >= 60`. |
| 80C deduction not capped | Logic bug | 52-53 | 2,00,000 of 80C was fully deducted; the legal limit is 1,50,000. | Capped 80C with `LIMIT_80C`. |
| PAN validation accepts trailing junk | Logic bug | 70-74 | `re.match` anchors only at the start, so "ABCDE1234FXYZ" was valid. | `re.fullmatch` on a compiled pattern. |
| Old regime missing Section 87A rebate | Logic bug | 50-61 | README says the program handles the rebate, but the old regime had none. | Tax is 0 when taxable income is at most 5,00,000. |
| Leftover debug print with side effect | Quality | 60 | `print("Last slab rate applied")` ran on every call and reused the loop variable after the loop. | Removed. |
| AES in ECB mode | Security, Medium (Bandit B305) | 77 | ECB is deterministic: the same PAN always gives the same ciphertext (confirmed by `True` output) and leaks patterns. | AES-GCM with a random 12-byte nonce. |
| Hard-coded encryption key | Security (not flagged by Bandit) | 15 | `PAN_KEY` sat in source code and in the repo history. | Read from `PAN_KEY_HEX` environment variable; random key if unset. |
| 1024-bit RSA key | Security, Medium (Bandit B505) | 83 | Below the 2048-bit minimum. | `key_size=2048`. |
| Unsafe XML parsing with minidom | Security, Medium/Low (B318, B408) | 5, 86 | Vulnerable to entity-expansion and similar XML attacks. | `defusedxml.minidom`. Added checks for missing tags. |
| CGIHandler (httpoxy) | Security, High (B412) | 6, 92 | CGI exposes the `Proxy` header as `HTTP_PROXY`. | Remove `HTTP_PROXY` before running; `# nosec B412` with that justification. |
| Bare `except` | Quality (E722, W0702) | 73 | Hides every error. | Removed the try/except; `isinstance` check instead. |
| `main()` runs on import | Quality | 106 | No `__main__` guard. | Added `if __name__ == "__main__":`. |
| Unused imports, variables, arguments | Quality (F401, F841, W0611, W0612, W0613) | 2-4, 36, 85, 91 | `os`, `sys`, `json`, `bracket`, `checked`, `strict`, `debug` unused. | Removed (`os` is now used). |
| Naming, docstrings, line length, spacing | Style (C0103, C0116, E501, E302, E305, C0209) | many | camelCase names, no docstrings, long lines, f-strings. | snake_case, docstrings, wrapped lines, f-strings. |

## Results after fixes

| Tool | Before | After |
| ---- | ------ | ----- |
| Pylint | 4.57/10 | 10.00/10 |
| Bandit | 6 issues (2 High, 3 Medium, 1 Low) | 0 |
| Flake8 | 23 warnings | 0 |
