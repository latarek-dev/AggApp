import { http, createConfig } from 'wagmi'
import { arbitrum } from 'wagmi/chains'
import { injected, metaMask, walletConnect } from 'wagmi/connectors'

export const config = createConfig({
  chains: [arbitrum],
  connectors: [
    injected(),
    metaMask(),
  ],
  transports: {
    [arbitrum.id]: http(),
  },
})