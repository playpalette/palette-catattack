import streamlit as st
import pandas as pd
import numpy as np
from web3 import Web3
from datetime import datetime, timezone

# Set global cache time - 15 minutes i.e. 900s
CACHE_TIME = 900

# Connect to the Base Goerli testnet
rpc_endpoint = 'https://goerli.base.org'
w3 = Web3(Web3.HTTPProvider(rpc_endpoint))

# Check if connected to Ethereum node
if not w3.is_connected():
    st.error("Error: Unable to connect to the Ethereum node.")
    st.stop()

# Set the contract address and ABI (Application Binary Interface)
contract_address = Web3.to_checksum_address("0xddb6dcce6b794415145eb5caa6cd335aeda9c272")

# Use the provided ABI
contract_abi = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "player",
                "type": "address"
            }
        ],
        "name": "getScore",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Create the contract object
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Define the function to get the score for an address - global cache time
@st.cache_data(ttl=CACHE_TIME)
def get_score(address):
    score = contract.functions.getScore(Web3.to_checksum_address(address)).call()
    return score

# Define the Streamlit app and title bar
st.set_page_config(page_title="Palette x CatAttack: a whitelist experiment by Palette", page_icon="./images/favicon.ico", layout="centered")
st.title(":cat: :crossed_swords: Palette x CatAttack: a whitelist experiment by Palette")
st.info('The data on this Streamlit dashboard is updated every 15 minutes. Real-time results may not be instantly reflected.')
st.warning('We recommend that you use a brand new wallet address for this experiment, to preserve your privacy and security, as this address may be doxxed via the public leaderboard.')

# Introduction
st.header("A whitelist experiment you say?")
st.markdown("""
            Palette is a non-profit open art experiment made for everyone. Our first NFT drop, Palette Pals, will be a whitelisted free mint with a limited supply, launching in May 2023.
            Before the official launch of Palette, we're giving away 765 lucky players early access via Palette Pal NFTs. This CatAttack experiment is the first of many ways to get a whitelist spot.
            """)
st.divider()
st.subheader("How do I get whitelisted?")
st.markdown("""
            * [**Register**](https://forms.gle/KBbofahYryGduYwr7) to play our CatAttack whitelist experiment
            * Play [**CatAttack**](https://mirror.xyz/0x554c1f09bf0907326C6e1eAde047E8A22382Eebb/p2fPsG5DfsA_gxsvj-g3wyUsDG9tV_c9_x7NTzIdriI) on the Base Goerli testnet (if you need testnet ETH, just ask us on [**Discord**](https://discord.gg/PDDt2BJaBe))
                * CatAttack is a free-to-play game on the Base Goerli testnet created by [**Joaquim**](https://twitter.com/joenrv) and the team at [**thirdweb**](https://thirdweb.com/)
                * Here's the link to the [**CatAttack page**](https://catattacknft.vercel.app/)
            * Get as high a score as you can before our timer runs out (10.05.2023 23:59:59 UTC)
            * 25 whitelist spots to be won by the top scorers
                * If you're an **OG** (and already have a whitelist spot), you can yourself get a second one (or give it away)!
            
            [Click here to learn more about **Palette**](https://linktr.ee/palette_base)
            """)
st.info('If you are wondering what wallet to use, check out [**Coinbase Wallet**](https://www.coinbase.com/wallet).')
st.divider()

# Set the target end time and calculate the time remaining
end_time = datetime(2023, 5, 10, 23, 59, 59, tzinfo=timezone.utc)
time_remaining = end_time - datetime.now(timezone.utc)

# Format the time remaining as days, hours, minutes, seconds
total_seconds = time_remaining.total_seconds()
days = int(total_seconds // (3600 * 24))
hours = int(total_seconds // 3600 % 24)
minutes = int(total_seconds // 60 % 60)
seconds = int(total_seconds % 60)

# Format the time remaining as bold, centered text and display the countdown
countdown_text = f"<p style='text-align: center; font-size: 36px'><strong>{days} days, {hours} hours, {minutes} minutes, {seconds} seconds remaining</strong></p>"
st.markdown(countdown_text, unsafe_allow_html=True)
st.divider()

# Set the target Ethereum addresses - global cache time
@st.cache_data(ttl=CACHE_TIME)
def load_target_addresses(gsheet_url):
    return pd.read_csv(gsheet_url)

gsheet_url = "https://docs.google.com/spreadsheets/d/1VMfkvB5eLI8xDc5Pi8PJ8_AQrD8qYxBx24FCTQr1iH0/export?format=csv&gid=2106651511"
df = load_target_addresses(gsheet_url)

target_addresses = df['What is your Base testnet address (e.g. 0xABC....)'].tolist()

# Allow the user to input Ethereum addresses
address_input = st.text_input("Enter an Ethereum (Base Goerli testnet) address and check its score:", placeholder="e.g. 0x1234...")

# Display the score for each address
score_displayed = False
for target_address in target_addresses:
    if address_input == target_address:
        score = get_score(address_input)
        st.write(f"The score for address {address_input} is: {score}")
        score_displayed = True

if not score_displayed and address_input:
    st.warning("You entered an address that has not been registered for this experiment. To participate, please register first. Otherwise, wait up to 15 minutes and if the error persists contact us on [**Discord**](https://discord.gg/PDDt2BJaBe).")
st.divider()

# Get scores for target addresses
data = []
for address in target_addresses:
    score = get_score(address)
    data.append({"address": address, "score": score})

# Create leaderboard table sorted by score in descending order, limited to the top 50 scores, with position column
df = pd.DataFrame(data)
df = df.sort_values(by=["score"], ascending=False)
df = df.head(50)
df["position"] = np.arange(1, len(df)+1)
df = df[["position", "address", "score"]]
df = df.style.set_properties(subset=['position'], **{'text-align': 'left'})

# Display leaderboard table
st.subheader("Leaderboard: only the top 25 get whitelisted")
st.table(df)
st.divider()

# Banner image
st.image("./images/banner_palette.png", use_column_width=True)
