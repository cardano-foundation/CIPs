# Run the demo

## Prerequirements

* node>=16.x.x, npm>=8.x.x

## Getting Started

```zsh
cd ionic-app
npm i
```

## Run the server (aka dApp)

Open the dApp.html file & your dev tools to see the console log outputs.

## Run the client (aka Wallet App)

```zsh
cd ionic-app
npm start
```

## Testing (PoC)

Once you have the server and client running you should see something like 

```js
"[info]: injected api of boostwallet into window.cardano"
```

in your dApp logs. Now you can issue

```js
window.cardano.boostwallet.getRewardAddresses().then(result => console.log(result))
```

to execute the remote call and get the reward address from your Wallet App.

