import streamlit as st
import pandas as pd
import random
import os
import numpy as np
from PIL import Image


def roll(value):
    return random.randint(1, value)

def subtract_value(row, value):
    # Subtract the value from the last column of the row
    row[-2] -= value
    return row

def load_data(encounter_name, player_iniative, enemies, players_ac, roll_colletivly):
    df_enemies = pd.read_excel("Data\Enemies.xlsx", index_col=0)
    df_players = pd.read_excel("Data\Players.xlsx", index_col=0)
    df_skills = pd.read_excel("Data\Skills.xlsx", index_col=0)
    enemie_names = []
    for x, y in enemies.items():
        for i in range(y):
            enemie_names += [f"{x}_{i}"]

    if os.path.exists(encounter_name):
        initative_order = pd.read_csv(encounter_name, index_col=0)
    else:
        if roll_colletivly:
            initative = roll(20)
            initative_order = pd.DataFrame(player_iniative + [[enemy, initative, df_enemies.loc[enemy.split("_")[0],"HP"], 0] for enemy in  enemie_names])
        else:
            initative_order = pd.DataFrame(player_iniative + [[enemy, roll(20), df_enemies.loc[enemy.split("_")[0],"HP"], 0] for enemy in  enemie_names])
        
        initative_order.columns = ['Name', 'ini', 'HP', 'Turn']
        initative_order = initative_order.round(0)
        initative_order = initative_order.sort_values(by=['ini'], ascending=False)
        initative_order = initative_order.reset_index(drop=True)
        initative_order.to_csv(encounter_name)
    
    return df_enemies, df_players, df_skills, initative_order, enemie_names, players_ac


def highlight_row(row):
    return ['background-color: yellow' if row.name == initative_order["Turn"][0] else '' for _ in row]

def next_turn_but_func(initative_order, file_name):
    initative_order["Turn"] = (initative_order["Turn"][0] + 1) % len(initative_order)
    initative_order.to_csv(file_name)

def display_dataframe_with_buttons(initative_order, file_name):
    """Displays the dataframe initative_order row for row with a button and text field next to it. 
    If the button is pressed it applies the value in the texfield to the last column of the row the button and textfield are on."""

    # Display the next turn button
    if st.button("Next Turn"):
        next_turn_but_func(initative_order, file_name)

    # Display the dataframe
    df_col, applying_col = st.columns([1,1])
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
                        initative_order.to_csv(file_name)
                        initative_order = pd.read_csv(file_name, index_col=0)

def roll_damage(base):
    display_text = ""
    for attack in base.split(":"):
        damage = 0
        dice_nmbr = int(attack.split("d")[0])
        dice_sort = int(attack.split("d")[1].split("+")[0])
        for dice_roll in range(dice_nmbr):
            damage += roll(dice_sort)
        damage += int(attack.split(",")[0].split("+")[1])
        damage_type = attack.split(",")[1]
        display_text += f"{damage} {damage_type} damage dealt,\n"
    return display_text

def display_enemie_select(df_enemies, df_skills, enemie_names, players_ac):
    """Adds two collumns. In the first collum displays a radio button for every enemey. In the second collum displays buttons for every skill of the enmey."""
    # Add two collumns
    display_text = "No attacks yet"
    col1, col2, col3 = st.columns([1,1, 1])
    with col1:
        # Display the radio buttons
        enemie = st.radio("Select Enemie", enemie_names)
    
    with col2:
        target = st.radio("Select Target", players_ac.keys())
    
    with col3:
        # Display the buttons for the skills
        row = df_enemies.loc[enemie.split("_")[0]]
        row = row[[f"Action_{i}" for i in range(1, 11)]].dropna()
        
        for skill in row:
            if st.button(skill):
                skill_chosen = df_skills.loc[skill]
                print(skill_chosen)
                ac = players_ac[target]
                if skill_chosen["Check if Hit"] == True:
                    rolled = roll(20)
                    hit_bonus = int(skill_chosen["Bonus to hit"])
                    to_hit = rolled + hit_bonus
                    base = skill_chosen["Base_damage"]
                    if to_hit >= ac:
                        display_text = f"Hit! {roll_damage(base)}, Rolled a {str(rolled)} With a bonus of {str(hit_bonus)} resulting in {str(to_hit)} against an AC of  {str(ac)}"
                        if type(skill_chosen["Damage_on_failed_save"]) == str and "d" in skill_chosen["Damage_on_failed_save"]:
                            display_text += f"\nand the player needs to make a  {skill_chosen['saving_trow_mod']} save with a ac of {skill_chosen['Saving_trow_dc']} taking {skill_chosen['Damage_on_failed_save']} ({roll_damage(skill_chosen['Damage_on_failed_save'])}) damage on a failed save or {skill_chosen['Damage_on_succes']} on a succes."
                            #if skill_chosen["Condition_on_failed_save"] != None and type(skill_chosen["Saving_trow_mod"]) != np.nan:
                            display_text += f"\n and be affected by the {skill_chosen['Condition_on_failed_save']} condition on a failed save."
                            
                    else:
                        display_text = f"Miss! No damage. Rolled a {str(rolled)} With a bonus of {str(hit_bonus)} resulting in {str(to_hit)} against an AC of  {str(ac)}"
    
    st.divider()
    col4, col5= st.columns([3,1])
    with col4:
        # selected_enemy = df_enemies.loc[enemie.split("_")[0]]
        # st.title(enemie.split("_")[0])
        # st.text(f"HP: {selected_enemy['HP']}, AC: {selected_enemy['AC']}, Speed: {selected_enemy['Speed']}")
        # st.text(f"STR:{selected_enemy['Str']}, DEX:{selected_enemy['Dex']}, CON:{selected_enemy['Con']}, INT:{selected_enemy['Int']}, WIS:{selected_enemy['Wis']}, CHA:{selected_enemy['Cha']}")
        # st.divider()
        # st.text(f"Saving Throws: {selected_enemy['Saving Throws']}")
        # st.text(f"Skills: {selected_enemy['Skills']}")
        # st.text(f"Damage Vulnerabilities: {selected_enemy['Vulnerabilities']}")
        # st.text(f"Damage Resistances: {selected_enemy['Resistances']}")
        # st.text(f"Damage Immunities: {selected_enemy['Immunities']}")
        # st.divider()
        statblock_url = "Data/stablocks/" + df_enemies.loc[enemie.split("_")[0]]["Statblock_link"]
        st.image(Image.open(statblock_url), caption='Statblock')
    
    with col5:
        st.write(display_text)


if __name__ == "__main__":
    players_ac = {"Lazarus": 18, "Abi": 16, "Lika": 16, "Bart": 16, "Goblin Berserker": 14, "Goblin Knight": 18, "Goblin Spy": 12}
    enemies = {"Caleb": 1, "Elyse": 1, "Goblin Berserker": 5}
    player_iniative = [["Lazarus", 0, 1, 0] ,["Abi", 0, 1, 0], ["Lika", 0, 1, 0]]
    file_name = "test_1.csv"
    roll_colletivly = True
    
    df_enemies, df_players, df_skills, initative_order, enemie_names, players_ac = load_data(file_name, player_iniative, enemies, players_ac, roll_colletivly)
    display_dataframe_with_buttons(initative_order, file_name)
    st.divider()
    display_enemie_select(df_enemies, df_skills, enemie_names, players_ac)

