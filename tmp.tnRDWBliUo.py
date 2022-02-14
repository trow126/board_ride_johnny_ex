import asyncio
import pybotters
from rich.pretty import pprint

SYMBOL = "BTCUSDT"
SIDE = "Buy" # Buy or Sell
LOT = 0.001

async def main():
    async with pybotters.Client(base_url="https://api.bybit.com") as client:
        # initialize
        store = pybotters.BybitUSDTDataStore()
        await store.initialize(
            client.get("/private/linear/order/search", params={"symbol": SYMBOL}),
            client.get("/private/linear/position/list", params={"symbol": SYMBOL}),
        )
        wstasks = await asyncio.gather(
            client.ws_connect(
                "wss://stream.bybit.com/realtime_public",
                send_json={
                    "op": "subscribe",
                    "args": [f"orderBookL2_25.{SYMBOL}"],
                },
                hdlr_json=store.onmessage,
            ),
            client.ws_connect(
                "wss://stream.bybit.com/realtime_private",
                send_json={"op": "subscribe", "args": ["position", "order"]},
                hdlr_json=store.onmessage,
            ),
        )

        # waiting loop
        while not len(store.orderbook):
            await store.orderbook.wait()

        # main loop
        while True:
            ob = {k: next(iter(v)) for k, v in store.orderbook.sorted().items()}
            od = next(iter(store.order.find(query={"symbol": SYMBOL})), None)
            pos = store.position.one(SYMBOL)
            # to entry
            if float(pos["size"]) < LOT or pos["side"] != SIDE:
                # no order
                if not od:
                    pprint("Place order")
                    task = asyncio.create_task(store.order.wait())
                    r = await client.post(
                        "/private/linear/order/create",
                        data={
                            "symbol": SYMBOL,
                            "side": SIDE,
                            "order_type": "Limit",
                            "qty": LOT,
                            "price": ob[SIDE]["price"],
                            "time_in_force": "PostOnly",
                            "close_on_trigger": False,
                            "reduce_only": False,
                            "position_idx": 0,
                        },
                    )
                    data = await r.json()
                    pprint(data)
                    if data["ret_code"] == 0:
                        pprint("Waiting for ws data...")
                        await task
                        pprint("Received")
                    else:
                        task.cancel()
                # order exists
                else:
                    # is not best price
                    if float(od["price"]) != float(ob[SIDE]["price"]):
                        pprint("Replace order")
                        task = asyncio.create_task(store.order.wait())
                        order_id = od["order_id"]
                        r = await client.post(
                            "/private/linear/order/replace",
                            data={
                                "order_id": order_id,
                                "symbol": SYMBOL,
                                "p_r_price": ob[SIDE]["price"],
                            },
                        )
                        data = await r.json()
                        pprint(data)
                        if data["ret_code"] == 0:
                            pprint("Waiting for ws data...")
                            await task
                            pprint("Received")
                        else:
                            task.cancel()
                    # is best price
                    else:
                        pass
            # position exists
            else:
                pprint("Position exists, exit")
                break

            # wait
            await store.orderbook.wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass