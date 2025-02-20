from agents.core.tbow_tactic_agent import TbowTacticAgent

if __name__ == "__main__":
    agent = TbowTacticAgent()

    print("🔵 Tbow Tactic AI Trading Bot")
    print("1. Generate Trade Plan")
    print("2. Schedule Automated Updates")
    print("3. Exit")

    while True:
        choice = input("Enter your choice: ")
        if choice == "1":
            symbol = input("Enter stock symbol: ").upper()
            result = agent.solve_task("generate_trade_plan", symbol=symbol)
            print(result)
        elif choice == "2":
            interval = int(input("Enter update interval (minutes): "))
            agent.solve_task("schedule_updates", interval=interval)
            print("✅ Auto-updates scheduled.")
        elif choice == "3":
            agent.shutdown()
            break
        else:
            print("⚠️ Invalid choice.")
