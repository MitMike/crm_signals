export default [
    {
        ignores: ["node_modules/**", "playwright-report/**", "test-results/**"],
    },
    {
        files: [
            "crm_signals/crm_signals/page/**/*.js",
            "crm_signals/public/js/**/*.js",
        ],
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "script",
            globals: {
                frappe: "readonly",
                $: "readonly",
                jQuery: "readonly",
                __: "readonly",
                cur_list: "readonly",
                window: "readonly",
                document: "readonly",
                console: "readonly",
            },
        },
        rules: {
            "no-undef": "error",
            "no-unused-vars": ["error", { args: "none", caughtErrors: "none", varsIgnorePattern: "^_" }],
            "no-unreachable": "error",
            "no-constant-condition": "error",
            "no-dupe-keys": "error",
            "no-func-assign": "error",
            "no-unexpected-multiline": "error",
            "no-debugger": "error",
            "no-alert": "error",
            eqeqeq: ["error", "always"],
        },
    },
];
