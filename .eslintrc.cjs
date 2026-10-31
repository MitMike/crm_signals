module.exports = [
    {
        ignores: ["node_modules/**", "**/dist/**"],
    },
    {
        files: ["**/*.js"],
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "script",
            globals: {
                frappe: "readonly",
                $: "readonly",
                __: "readonly",
                console: "readonly",
                window: "readonly",
                document: "readonly",
            },
        },
        rules: {
            "no-undef": "error",
            "no-unreachable": "error",
            "no-constant-condition": "error",
            "no-dupe-keys": "error",
            "no-duplicate-case": "error",
            "no-empty": ["error", { allowEmptyCatch: false }],
            "no-eval": "error",
            "no-implied-eval": "error",
            "no-new-func": "error",
            "no-debugger": "error",
            "no-var": "error",
            "prefer-const": "error",
            eqeqeq: ["error", "always"],
        },
    },
];
