# Lab 5 Reflection: Static Code Analysis

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest issues were the style and quality warnings from Pylint and Flake8. Removing the unused imports (`os`, `sys`, `json`) and unused variables (`bracket`, `checked`), renaming camelCase functions to snake_case, adding docstrings and wrapping long lines were all mechanical. The tool gave the exact line and the fix was obvious. Changing `key_size=1024` to `2048` and replacing `minidom` with `defusedxml` were also one-line fixes.

The hardest issues were the logic bugs, because no tool reported them. The program ran without errors and printed numbers, so I only found the problems by checking whether the output made sense. The new-regime function taxed the whole income at one flat rate, so 18,00,000 gave 358,800 when the correct figure is 150,800. The rebate used `<` instead of `<=`, so 12,75,000 paid 124,800 instead of 0. `betterRegime` had its comparison inverted and picked the more expensive regime. `basicExemption` used `age > 80`, so an 80-year-old got the wrong limit. I had to work out what the correct tax should be and trace the code against it. Fixing the flat-rate bug also meant restructuring the code around a shared progressive-tax function, which removed the "too many return statements" warning along the way.

The Bandit finding on `CGIHandler` (B412, High) was also hard, because there was no simple replacement. I had to understand the httpoxy attack to decide on a mitigation.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

Yes, partly. Bandit reported B412 on `CGIHandler`, which is a real concern in general: in CGI mode the `Proxy` header becomes the `HTTP_PROXY` environment variable. However, Bandit reports it on the import line and on the call regardless of what the code does, so it still fires after the risk is handled. I removed `HTTP_PROXY` from the environment before running the handler, and then had to suppress the warning with `# nosec B412`. Bandit cannot see that the mitigation is there, so the warning remains even when the code is safe.

The XML warnings (B318, B408) are similar in this program, because `main()` only parses a hard-coded string. They are not exploitable here, but they would be as soon as the function receives a real uploaded Form-16, so I fixed them anyway.

The reverse also happened: some real problems were not reported at all. Bandit did not flag the hard-coded `PAN_KEY` because its secret check looks at names like `password` and `token`. It is not a perfect list of problems either way.

## 3. How would you integrate static analysis tools into your actual software development workflow?

I would run them at three points:

- **In the editor:** Pylint and Flake8 run as I type, so style and unused-code problems are fixed immediately.
- **As a pre-commit hook:** Flake8, Pylint and Bandit run before each commit, so problems never enter the repository.
- **In CI:** the same three tools run on every pull request (for example with GitHub Actions), and the merge is blocked on a failure or a score below a set threshold such as 9.5.

I would pin the tool versions and keep one shared config file, so results are the same for everyone. Suppressions like `# nosec` should need a written reason and a reviewer's approval. I would also treat the tools as a first filter only. They need to be combined with unit tests (for example, a test that the tax on 12,00,000 taxable income is 0) and code review, because this lab showed they miss logic errors.

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Scores:** Pylint went from 4.57/10 to 10.00/10, Bandit from 6 issues (2 High, 3 Medium, 1 Low) to 0, and Flake8 from 23 warnings to 0.
- **Correctness:** the tax figures are now sensible, with 12,75,000 giving 0 and 18,00,000 giving 150,800 under the new regime. The better regime is now chosen correctly, and invalid PANs are rejected.
- **Readability:** snake_case names, docstrings on every function, named constants and slab tables replaced a long if/elif chain, and shared logic lives in one `_progressive_tax` function instead of being duplicated.
- **Security:** PANs are encrypted with AES-GCM and a random nonce, so the same PAN no longer gives the same ciphertext. The key now comes from an environment variable, the RSA key is 2048-bit, and XML is parsed safely.
- **Robustness:** the bare `except` is gone, missing XML tags give a clear error, and importing the module no longer runs `main()` because of the `__main__` guard.
