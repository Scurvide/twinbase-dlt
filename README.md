# Twinbase DLT

Twinbase is an open-source platform for implementing [Semantic Twins](https://github.com/IoT-NGIN/guide-to-semantic-twins).
In particular, Twinbase helps to manage and distribute [digital twin documents](https://doi.org/10.1109/ACCESS.2020.3045856).
It is built on git and can be hosted on free-of-charge GitHub services.
This new DLT (distributed ledger technology) version of Twinbase supports anchoring the history of twin documents into a distributed ledger.

See an example server live at [dtw.twinbase.org](https://dtw.twinbase.org) and details in an open access journal article: Autiosalo, J., Siegel, J., Tammi, K., 2021. Twinbase: Open-Source Server Software for the Digital Twin Web. IEEE Access 9, 140779–140798. https://doi.org/10.1109/ACCESS.2021.3119487

Twinbase is at __*initial development*__ phase and backwards incompatible changes may occur.
Update mechanisms are not yet implemented.

Twinbase is hosted by Aalto University where its development was initiated as a result of the experience from multiple digital twin related projects.
Twinbase is used as a tool for building the Digital Twin Web introduced in Section III of [this article](https://doi.org/10.1109/ACCESS.2020.3045856).
Experiences with Twinbase are used to develop further versions of the [digital twin document standard](https://github.com/AaltoIIC/dt-document).

## Using Twinbase

You can browse the web interface of this Twinbase from the URL shown on the `baseurl` field in the [/docs/index.yaml](/docs/index.yaml) file if this Twinbase is properly configured.

You can fetch twin documents in Python with the [dtweb-python](https://github.com/juusoautiosalo/dtweb-python) library. Available as `dtweb` from pip.

## To create your own Twinbase

1. Create a new repository with the "Use this template" button on the [twinbase/twinbase](https://github.com/twinbase/twinbase) page. (Sign in to GitHub if you can't see the button.)
2. Make GitHub Actions work
    1. In the newly created repository, activate GitHub Actions from the Actions tab (if necessary).
    2. From Settings > Actions > General > Workflow permissions, activate "Read and write permissions" and save. (This allows GitHub actions to push to this repository.)
    3. Manually run the "File modifier" workflow from: Actions > File Modifier > Run Workflow > Run workflow. (This will modify the files to match your GitHub account. Running the workflow several times will not cause any harm.)
3. Activate GitHub Pages from Settings > Pages:
    1. Source: "Deploy from a branch"
    2. Branch: Select `main` and `/docs` and save.
4. A link to the web interface of Twinbase will be shown at the Pages page. If you have not made any domain name customizations, it is in the form *\<username\>.github.io/\<repository name\>*.
5. Updates: Unfortunately any updates from the template repository must currently be made manually. But you can also just make another Twinbase and copy your twin folders and files there.

Forks are not recommended for creating a Twinbase instance.

### Creating new twins to your Twinbase

Recommended method to create new twins is to use the new-twin page found on the front page of each Twinbase.

After creating a twin, you need to activate its DT identifier with one of these methods: 
   - To activate the automatically generated dtid.org identifier, send the values of dt-id and hosting-iri of each twin to [this form](https://dtid.org/form).
   - Or you can overwrite the dt-id with the URL given by any [URL shortener service](https://en.wikipedia.org/wiki/URL_shortening#Services) or the [perma-id](https://github.com/perma-id/w3id.org) service. The URL needs to redirect to the hosting-iri.

## To start developing Twinbase

Contribution guidelines are not yet established, but useful contributions are welcome! For development, you can try this:
1. Create your own Twinbase using the Template.
2. Modify your Twinbase as you wish in GitHub.
3. Fork [twinbase/twinbase](https://github.com/twinbase/twinbase). (Do not activate Actions to avoid unnecessary commits.)
4. Manually copy the useful modifications from the repository created with the Template.
5. Submit a pull request.

Local development is a bit tricky as Twinbase uses GitHub Actions as an intergal part of the platform, but feel free to try!

## Store hashes of twin documents to an Ethereum distributed ledger
Hashes of twin documents (`index.json`) can be stored to a DLT (distributed ledger technology) for later verification of the integrity of the document. Hashes may be stored to a DLT with GitHub Actions.

To make the DLT functionality work, you need to define following information:
- `DLT_TYPE`
  - Name of DLT, for example `Ethereum Sepolia Testnet`. This is used to sufficiently describe the DLT that is being used so that it can be found by a human verifying the document later.
- `DLT_HTTP_NODE`
  - DLT HTTP endpoint. You can create one at various node providers for free, for example, [Infura](https://www.infura.io/).
- `DLT_PRIVATE_KEY`
  - Combined "identity and password" for an [Ethereum account](https://ethereum.org/en/developers/docs/accounts/) (i.e. private key) with some currency for transaction fees. You can create one e.g. with python [web3.py library](https://web3py.readthedocs.io/en/stable/web3.eth.account.html#creating-a-private-key). You can add currency to you account e.g. [here](https://sepolia-faucet.pk910.de/).
- `DLT_GAS_PROVIDED`
  - Maximum gas limit that is provided with transactions. The realized gas usage depends on the difficulty of mining the transaction. Current gas market price against ether is calculated in the script. [Gas and fees info](https://ethereum.org/en/developers/docs/gas/).
- `DLT_AUTOMATIC`
  - Set to `true` to send hashes to DLT automatically when a DT document is modified or created. Otherwise, send hashes manually by running the `Submit twin document hash to DLT` workflow from the `Actions` tab.
  - Allowed values: `true` or `false`

These secrets and variables are set in the repository settings on GitHub under  
 `Settings` > `Secrets and variables` > `Actions`.
 > **Note**
 > These can be set only by users with Admin access to the repository.
   - Set `DLT_PRIVATE_KEY` as `New repository secret`.
   - Set `DLT_HTTP_NODE`, `DLT_TYPE`, `DLT_GAS_PROVIDED` and `DLT_AUTOMATIC` as `Variables` > `New repository variable`.

Examples of the GitHub secrets and variables required:
```
# Repository secrets:
DLT_PRIVATE_KEY=0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

# Repository variables:
DLT_TYPE="Ethereum Sepolia Testnet"
DLT_HTTP_NODE=https://sepolia.infura.io/v3/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DLT_GAS_PROVIDED=100000
DLT_AUTOMATIC=false
```

**Information of the transaction and hash is stored to a `hash-info.json` file within the twin folder.** The value `transactionHash` in this file can be used to discover the transaction within the DLT. The hash found in the DLT transaction as `input` should match the `twinHash` value found in `hash-info.json`.

## Support

There are currently no official support mechanisms for Twinbase, but [Juuso](https://juu.so) may be able to help.

## Thanks

Python: See `requirements.txt` and `dev.in`

JavaScript: Twinbase uses
- [mini.css](https://minicss.org/) to stylize web pages and 
- [json-view](https://github.com/pgrabovets/json-view) to display digital twin documents.
- [web3.js](https://github.com/web3/web3.js) to perform crypto operations in the browser.
  (Version [1.8.2](https://github.com/web3/web3.js/blob/632c5d3a7b91eeb436f043311db6350f950b3dda/dist/web3.min.js))

Thanks to the developers for the nice pieces of software!
