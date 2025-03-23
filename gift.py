from web3 import Web3
import asyncio
import json
import requests
import time

web3 = Web3(Web3.WebsocketProvider('ws://176.9.26.139:8546'))

WALLET_ADDRESS = '0x4982085c9e2f89f2ecb8131eca71afad896e89cb'
BOT_TOKEN = '7745888483:AAFjmPGRHJmk3GnxPEwRWlXRzUKq1YsI4Vs'
CHANNEL_ID = '-1002501391473'

known_recipients = set()

def send_telegram_message(message):
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        data = {
            'chat_id': CHANNEL_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram Error: {e}")

async def handle_event(event):
    try:
        tx = web3.eth.get_transaction(event)

        if tx and tx.to and tx['from'].lower() == WALLET_ADDRESS.lower():
            if tx.to.lower() not in known_recipients:
                known_recipients.add(tx.to.lower())

                value = web3.from_wei(tx.value, 'ether')

                message = (
                    '🚨 <b>New Transaction Detected!</b>\n\n'
                    f'💰 Amount: {value} BNB\n'
                    f'📤 From: <code>{tx["from"]}</code>\n'
                    f'📥 To: <code>{tx.to}</code>\n'
                    f'🔗 Hash: <code>{tx.hash.hex()}</code>\n\n'
                    f'🔍 <a href="https://bscscan.com/tx/{tx.hash.hex()}">View on BSCScan</a>'
                )

                send_telegram_message(message)

                print('New recipient detected!')
                print('From:', tx['from'])
                print('To:', tx.to)
                print('Amount:', value, 'BNB') 
                print('Tx Hash:', tx.hash.hex())
                print('------------------------')

    except Exception as e:
        print(f"Error: {e}")

async def log_loop(event_filter):
    while True:
        try:
            for event in event_filter.get_new_entries():
                await handle_event(event)
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error in log loop: {e}")
            await asyncio.sleep(1)

def main():
    print('Monitoring transactions...')
    send_telegram_message('🟢 Monitor started\nWatching for new transactions...')

    tx_filter = web3.eth.filter('pending')

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(tx_filter)
            )
        )
    finally:
        loop.close()

if __name__ == '__main__':
    main()