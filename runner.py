import streamlit as st
import pandas as pd
import random
import os

def roll(value):
    return random.randint(1, value)

def subtract_value(row, value):
    # Subtract the value from the last column of the row
    row[-2] -= value
    return row

def load_data():
    df_enemies = pd.read_excel("Data\Enemies.xlsx", index_col=0)
    df_players = pd.read_excel("Data\Players.xlsx", index_col=0)
    df_skills = pd.read_excel("Data\Skills.xlsx", index_col=0)
    player_iniative = [["Lazarus",0, 1, 0] ,["Abi", 0, 1, 0], ["Lika", 0, 1, 0], ["Bart", 0, 1, 0]]
    players_ac = {"Lazarus": 18, "Abi": 16, "Lika": 16, "Bart": 16}
    enemies = {"Bandit": 4}
    enemie_names = []
    for x, y in enemies.items():
        for i in range(y):
            enemie_names += [f"{x}_{i}"]

    if os.path.exists("ini_order.csv"):
        initative_order = pd.read_csv("ini_order.csv", index_col=0)
    else:
        initative_order = pd.DataFrame(player_iniative + [[enemy, roll(20), df_enemies.loc[enemy.split("_")[0],"HP"], 0] for enemy in  enemie_names])
        initative_order.columns = ['Name', 'ini', 'HP', 'Turn']
        initative_order = initative_order.round(0)
        initative_order = initative_order.sort_values(by=['ini'], ascending=False)
        initative_order = initative_order.reset_index(drop=True)
        initative_order.to_csv("ini_order.csv")
    
    return df_enemies, df_players, df_skills, initative_order, enemie_names, players_ac


def highlight_row(row):
    return ['background-color: yellow' if row.name == initative_order["Turn"][0] else '' for _ in row]

def next_turn_but_func(initative_order):
    initative_order["Turn"] = (initative_order["Turn"][0] + 1) % len(initative_order)
    initative_order.to_csv("ini_order.csv")

def display_dataframe_with_buttons(initative_order):
    """Displays the dataframe initative_order row for row with a button and text field next to it. 
    If the button is pressed it applies the value in the texfield to the last column of the row the button and textfield are on."""

    # Display the next turn button
    if st.button("Next Turn"):
        next_turn_but_func(initative_order)

    # Display the dataframe
    df_col, applying_col = st.columns([2,1])
    with df_col:
        st.dataframe(initative_order.style.apply(highlight_row, axis=1))

    with applying_col:
        # Display the button and textfield next to the dataframe
        for index, row in initative_order.iterrows():
            if row["Name"] in enemie_names:
                but_col, text_col = st.columns([1,1])
                with text_col:
                    value = st.text_input(row["Name"], 0)
                with but_col:
                    if st.button(row["Name"]):
                        initative_order.iloc[index] = subtract_value(row, int(value))
                        initative_order.to_csv("ini_order.csv")
                        initative_order = pd.read_csv("ini_order.csv", index_col=0)

def roll_damage(base):
    display_text = ""
    for attack in base.split(":"):
        damage = 0
        for dice_roll in range(int(attack[0])):
            dice_nmbr = int(attack.split("+")[0][2:])
            damage += roll(dice_nmbr)
        damage += int(attack.split("+")[1].split(",")[0])
        damage_type = attack.split(",")[1]
        display_text += f"{damage} {damage_type} damage dealt,\n"

def display_enemie_select(df_enemies, df_skills, enemie_names, players_ac):
    """Adds two collumns. In the first collum displays a radio button for every enemey. In the second collum displays buttons for every skill of the enmey."""
    # Add two collumns
    display_text = "No attacks yet"
    col1, col2, col3 = st.columns([1,1, 1])
    with col1:
        # Display the radio buttons
        enemie = st.radio("Select Enemie", enemie_names)
    
    with col2:
        target = st.radio("Select Enemie", players_ac.keys())
    
    with col3:
        # Display the buttons for the skills
        row = df_enemies.loc[enemie.split("_")[0]]
        row = row[[f"Action_{i}" for i in range(1, 11)]].dropna()
        
        for skill in row:
            if st.button(skill):
                skill_chosen = df_skills.loc[skill]
                ac = players_ac[target]
                if skill_chosen["Check if Hit"] == True:
                    rolled = roll(20)
                    to_hit = rolled + skill_chosen["Bonus to hit"]
                    base = skill_chosen["Base_damage"]
                    
                    if to_hit >= ac:
                        display_text = "Hit! " + roll_damage(base)
                        if skill_chosen["Damage_on_failed_save"] != None:
                            display_text += f"\nand the player needs to make a  {skill_chosen['saving_trow_mod']} save with a ac of {skill_chosen['Saving_trow_dc']} taking {roll_damage}\ndamage on a failed save or {skill_chosen['Damage_on_succes']}."
                            if skill_chosen["Condition_on_failed_save"] != None:
                                display_text += f"\n and be affected by the {skill_chosen['Condition_on_failed_save']} condition on a failed save."
                            
                    else:
                        display_text = f"Miss! No damage dealt. Rolled a " + str(rolled) + " With a bonus of resulting in " + str(to_hit) + "\nagainst an AC of " + str(ac)
                else:
    st.text(display_text)





if __name__ == "__main__":
    df_enemies, df_players, df_skills, initative_order, enemie_names, players_ac = load_data()
    display_dataframe_with_buttons(initative_order)
    display_enemie_select(df_enemies, df_skills, enemie_names, players_ac)

