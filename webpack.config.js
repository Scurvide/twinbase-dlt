const path = require('path');

module.exports = {
    entry: './docs/static/contract/verify-twin.ts',
    output: {
        filename: 'verifier.js',
        path: path.resolve(__dirname, 'docs/static/contract')
    },
    resolve: {
        extensions: ['.ts', '.js']
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: 'ts-loader',
                exclude: /node_modules/
            }
        ]
    },
    mode: "production"
};