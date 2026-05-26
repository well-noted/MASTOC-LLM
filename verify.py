import pandas as pd

def check_asymmetric():
    print("=== TRAJECTORY FOR 20260516_203343_full-gabm ===")
    df = pd.read_csv("logs/20260516_203343_full-gabm/resources.csv")
    print(df[['tick', 'agent0_cows', 'agent1_cows', 'agent2_cows', 'pool_pct']])
    
    # Check decisions to see how many additions Agent 1 and Agent 2 made
    dec = pd.read_csv("logs/20260516_203343_full-gabm/decisions.csv")
    print("\nActions breakdown by agent:")
    for a in [0, 1, 2]:
        agent_dec = dec[dec['agent_id'] == a]
        print(f"Agent {a} actions count:")
        print(agent_dec['action_name'].value_counts())

check_asymmetric()
