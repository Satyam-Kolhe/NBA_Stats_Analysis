import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df_games = pd.read_csv('games.csv')
df_games_details = pd.read_csv('games_details.csv')
df_players = pd.read_csv('players.csv')
df_rankings = pd.read_csv('ranking.csv')
df_team = pd.read_csv('teams.csv')

df_games_details = df_games_details.merge(df_games[['GAME_ID', 'SEASON']], on='GAME_ID', how='left')

st.title('NBA Stats Overview (2014-2022)')
st.sidebar.title('DashBoard')

# Select team or player
selection = st.sidebar.selectbox('Choose:', ['Select', 'Team', 'Player'])
if selection == 'Team':
    # Update team list to include nickname and abbreviation
    team_list = df_team.apply(lambda x: f"{x['NICKNAME']} ({x['ABBREVIATION']})", axis=1).unique()
    team = st.sidebar.selectbox('Select Team:', ['Select'] + list(team_list))

    if team != 'Select':
        # Extract the abbreviation from the selected team
        team_abbr = team.split('(')[-1].strip(')')
        team_data = df_team[df_team['ABBREVIATION'] == team_abbr]

        if not team_data.empty:
            st.sidebar.title(f"Team: {team_data['NICKNAME'].values[0]} ({team_abbr})")
            section = st.sidebar.radio("Select Section:", ["General Info", "Match Details", "Rankings"])

            if section == "General Info":
                st.header(f"Statistics for {team_data['NICKNAME'].values[0]} ({team_abbr})")
                st.markdown(f"**City:** {team_data['CITY'].values[0]}")
                st.markdown(f"**Arena:** {team_data['ARENA'].values[0]}")

                # Select season
                season = st.sidebar.slider('Select Season:', 2014, 2022, 2022)
                team_id = team_data['TEAM_ID'].values[0]
                team_games = df_games[(df_games['HOME_TEAM_ID'] == team_id) | (df_games['VISITOR_TEAM_ID'] == team_id)]
                season_games = team_games[team_games['SEASON'] == season]

                if not season_games.empty:
                    season_games['DATE'] = pd.to_datetime(season_games['GAME_DATE_EST'])
                    season_games.sort_values('DATE', inplace=True)
                    season_games['RESULT'] = season_games.apply(
                        lambda row: 'Win' if (row['HOME_TEAM_ID'] == team_id and row['HOME_TEAM_WINS'] == 1) or (
                                row['VISITOR_TEAM_ID'] == team_id and row['HOME_TEAM_WINS'] == 0) else 'Loss', axis=1)
                    season_games['TEAM_POINTS'] = season_games.apply(
                        lambda row: row['PTS_home'] if row['HOME_TEAM_ID'] == team_id else row['PTS_away'], axis=1)
                    season_games['OPPONENT_POINTS'] = season_games.apply(
                        lambda row: row['PTS_away'] if row['HOME_TEAM_ID'] == team_id else row['PTS_home'], axis=1)
                    season_games['OPPONENT_TEAM'] = season_games.apply(
                        lambda row: df_team[df_team['TEAM_ID'] == (
                            row['VISITOR_TEAM_ID'] if row['HOME_TEAM_ID'] == team_id else row['HOME_TEAM_ID'])][
                                        'NICKNAME'].values[0] + " (" + df_team[df_team['TEAM_ID'] == (
                            row['VISITOR_TEAM_ID'] if row['HOME_TEAM_ID'] == team_id else row['HOME_TEAM_ID'])][
                                        'ABBREVIATION'].values[0] + ")", axis=1)

                    # Pie chart for total wins and losses
                    st.subheader(f"Total Wins and Losses for {team_data['NICKNAME'].values[0]} ({team_abbr}) in {season}")
                    wins = season_games['RESULT'].value_counts().get('Win', 0)
                    losses = season_games['RESULT'].value_counts().get('Loss', 0)
                    labels = ['Wins', 'Losses']
                    sizes = [wins, losses]
                    colors = ['#4CAF50', '#F44336']
                    explode = (0.1, 0)  # explode the 1st slice (Wins)

                    fig, ax = plt.subplots()
                    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                           shadow=True, startangle=140)
                    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                    st.pyplot(fig)
                    st.markdown(f"**Total Wins:** {wins} | **Total Losses:** {losses}")

                    # Line charts for win and loss percentages for each season
                    st.subheader(f"Win and Loss Percentages for {team_data['NICKNAME'].values[0]} ({team_abbr}) Across Seasons")
                    seasons = df_games['SEASON'].unique()
                    season_wins = []
                    season_losses = []
                    for s in seasons:
                        s_games = team_games[team_games['SEASON'] == s]
                        s_wins = s_games.apply(
                            lambda row: 1 if (row['HOME_TEAM_ID'] == team_id and row['HOME_TEAM_WINS'] == 1) or (
                                    row['VISITOR_TEAM_ID'] == team_id and row['HOME_TEAM_WINS'] == 0) else 0, axis=1).sum()
                        s_losses = len(s_games) - s_wins
                        season_wins.append(s_wins)
                        season_losses.append(s_losses)

                    win_percentages = [100 * wins / (wins + losses) if (wins + losses) > 0 else 0 for wins, losses in zip(season_wins, season_losses)]
                    loss_percentages = [100 - win_percentages[i] for i in range(len(win_percentages))]

                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                    ax1.plot(seasons, win_percentages, label='Win Percentage', marker='o', color='green')
                    ax1.set_xlabel('Season')
                    ax1.set_ylabel('Win Percentage')
                    ax1.set_title(f'Win Percentage for {team_data["NICKNAME"].values[0]} ({team_abbr}) Across Seasons')

                    ax2.plot(seasons, loss_percentages, label='Loss Percentage', marker='o', color='red')
                    ax2.set_xlabel('Season')
                    ax2.set_ylabel('Loss Percentage')
                    ax2.set_title(f'Loss Percentage for {team_data["NICKNAME"].values[0]} ({team_abbr}) Across Seasons')

                    fig.tight_layout()
                    st.pyplot(fig)

            elif section == "Match Details":
                st.header("Top 10 Teams Rankings")
                # Select season
                season = st.sidebar.slider('Select Season:', 2014, 2022, 2022)
                # Filter data based on the selected season
                season_games_details = df_games_details[df_games_details['SEASON'] == season]
                season_games = df_games[df_games['SEASON'] == season]
                team_id = team_data['TEAM_ID'].values[0]
                team_name = df_team[df_team['TEAM_ID'] == team_id]['NICKNAME'].values[0]
                team_games = df_games[(df_games['HOME_TEAM_ID'] == team_id) | (df_games['VISITOR_TEAM_ID'] == team_id)]
                season_games = team_games[team_games['SEASON'] == season]
                if not season_games.empty:
                    season_games['DATE'] = pd.to_datetime(season_games['GAME_DATE_EST'])
                    season_games.sort_values('DATE', inplace=True)
                    season_games['RESULT'] = season_games.apply(
                        lambda row: 'Win' if (row['HOME_TEAM_ID'] == team_id and row['HOME_TEAM_WINS'] == 1) or
                                             (row['VISITOR_TEAM_ID'] == team_id and row[
                                                 'HOME_TEAM_WINS'] == 0) else 'Loss', axis=1)
                    season_games['TEAM_POINTS'] = season_games.apply(
                        lambda row: row['PTS_home'] if row['HOME_TEAM_ID'] == team_id else row['PTS_away'], axis=1)
                    season_games['OPPONENT_POINTS'] = season_games.apply(
                        lambda row: row['PTS_away'] if row['HOME_TEAM_ID'] == team_id else row['PTS_home'], axis=1)
                    season_games['OPPONENT_TEAM'] = season_games.apply(
                        lambda row: df_team[df_team['TEAM_ID'] == (
                            row['VISITOR_TEAM_ID'] if row['HOME_TEAM_ID'] == team_id else row['HOME_TEAM_ID'])][
                                       'NICKNAME'].values[0] +
                                    " (" + df_team[df_team['TEAM_ID'] == (
                            row['VISITOR_TEAM_ID'] if row['HOME_TEAM_ID'] == team_id else row['HOME_TEAM_ID'])][
                                        'ABBREVIATION'].values[0] + ")", axis=1)
                    st.header("**Match Details:**")
                    matches_to_show = 3
                    # Line graph of matches
                    plt.figure(figsize=(10, 6))
                    plt.plot(season_games['DATE'], season_games['TEAM_POINTS'], marker='o', label='Team Points')
                    for i, row in season_games.iterrows():
                        plt.text(row['DATE'], row['TEAM_POINTS'], row['RESULT'], fontsize=8, ha='right')
                    plt.xlabel('Date (Day-Month)')
                    plt.ylabel('Points')
                    plt.title('Match Points Over Time')
                    plt.legend()
                    st.pyplot(plt)
                    if 'match_count' not in st.session_state:
                        st.session_state.match_count = matches_to_show
                    for index, row in season_games.iloc[:st.session_state.match_count].iterrows():
                        st.markdown(f"### {row['DATE'].strftime('%Y-%m-%d')}")
                        st.markdown(f"**{team_data['NICKNAME'].values[0]} ({team_abbr}) vs {row['OPPONENT_TEAM']}**")
                        st.markdown(
                            f"**Team Points:** {row['TEAM_POINTS']} | **Opponent Points:** {row['OPPONENT_POINTS']}")
                        st.markdown(f"**Result:** {row['RESULT']}")
                        # Include how the points were scored by each team
                        st.markdown("#### Points Breakdown")
                        team_game_details = df_games_details[df_games_details['GAME_ID'] == row['GAME_ID']]
                        home_team_details = team_game_details[team_game_details['TEAM_ID'] == row['HOME_TEAM_ID']]
                        away_team_details = team_game_details[team_game_details['TEAM_ID'] == row['VISITOR_TEAM_ID']]
                        team_points_breakdown = {
                            "Free Throws": home_team_details['FTM'].sum() if row['HOME_TEAM_ID'] == team_id else
                            away_team_details['FTM'].sum(),
                            "Field Goals": home_team_details['FGM'].sum() if row['HOME_TEAM_ID'] == team_id else
                            away_team_details['FGM'].sum(),
                            "Three Pointers": home_team_details['FG3M'].sum() if row['HOME_TEAM_ID'] == team_id else
                            away_team_details['FG3M'].sum(),
                        }
                        opponent_points_breakdown = {
                            "Free Throws": away_team_details['FTM'].sum() if row['HOME_TEAM_ID'] == team_id else
                            home_team_details['FTM'].sum(),
                            "Field Goals": away_team_details['FGM'].sum() if row['HOME_TEAM_ID'] == team_id else
                            home_team_details['FGM'].sum(),
                            "Three Pointers": away_team_details['FG3M'].sum() if row['HOME_TEAM_ID'] == team_id else
                            home_team_details['FG3M'].sum(),
                        }
                        points_breakdown_df = pd.DataFrame({
                            "Team": team_points_breakdown,
                            "Opponent": opponent_points_breakdown
                        }).T
                        st.table(points_breakdown_df)
                        st.markdown("---")
                    if st.session_state.match_count < len(season_games):
                        if st.button('Load More'):
                            st.session_state.match_count += 5

            elif section == "Rankings":
                st.header("Top 10 Teams Rankings")
                # Select season
                season = st.sidebar.slider('Select Season:', 2014, 2022, 2022)
                # Filter data based on the selected season
                season_games_details = df_games_details[df_games_details['SEASON'] == season]
                season_games = df_games[df_games['SEASON'] == season]
                team_id = team_data['TEAM_ID'].values[0]
                team_name = df_team[df_team['TEAM_ID'] == team_id]['NICKNAME'].values[0]
                # Points
                top_10_points = season_games_details.groupby('TEAM_ID').sum().nlargest(10, 'PTS')[['PTS']].reset_index()
                top_10_points = top_10_points.merge(df_team[['TEAM_ID', 'NICKNAME']], on='TEAM_ID')
                top_10_points = top_10_points.rename(columns={'PTS': 'Points', 'NICKNAME': 'Team Name'})
                top_10_points['Rank'] = top_10_points.index + 1
                top_10_points = top_10_points[['Rank', 'Team Name', 'Points']]
                team_rank_points = season_games_details.groupby('TEAM_ID').sum().reset_index().sort_values('PTS',
                                                                                                           ascending=False)
                team_rank_points['Rank'] = range(1, len(team_rank_points) + 1)
                selected_team_rank_points = team_rank_points[team_rank_points['TEAM_ID'] == team_id][
                    ['TEAM_ID', 'PTS', 'Rank']]
                selected_team_points = selected_team_rank_points.merge(df_team[['TEAM_ID', 'NICKNAME']],
                                                                       on='TEAM_ID').rename(
                    columns={'PTS': 'Points', 'NICKNAME': 'Team Name'})
                # Assists
                top_10_assists = season_games_details.groupby('TEAM_ID').sum().nlargest(10, 'AST')[
                    ['AST']].reset_index()
                top_10_assists = top_10_assists.merge(df_team[['TEAM_ID', 'NICKNAME']], on='TEAM_ID')
                top_10_assists = top_10_assists.rename(columns={'AST': 'Assists', 'NICKNAME': 'Team Name'})
                top_10_assists['Rank'] = top_10_assists.index + 1
                top_10_assists = top_10_assists[['Rank', 'Team Name', 'Assists']]
                team_rank_assists = season_games_details.groupby('TEAM_ID').sum().reset_index().sort_values('AST',
                                                                                                            ascending=False)
                team_rank_assists['Rank'] = range(1, len(team_rank_assists) + 1)
                selected_team_rank_assists = team_rank_assists[team_rank_assists['TEAM_ID'] == team_id][
                    ['TEAM_ID', 'AST', 'Rank']]
                selected_team_assists = selected_team_rank_assists.merge(df_team[['TEAM_ID', 'NICKNAME']],
                                                                         on='TEAM_ID').rename(
                    columns={'AST': 'Assists', 'NICKNAME': 'Team Name'})
                # Rebounds
                top_10_rebounds = season_games_details.groupby('TEAM_ID').sum().nlargest(10, 'REB')[
                    ['REB']].reset_index()
                top_10_rebounds = top_10_rebounds.merge(df_team[['TEAM_ID', 'NICKNAME']], on='TEAM_ID')
                top_10_rebounds = top_10_rebounds.rename(columns={'REB': 'Rebounds', 'NICKNAME': 'Team Name'})
                top_10_rebounds['Rank'] = top_10_rebounds.index + 1
                top_10_rebounds = top_10_rebounds[['Rank', 'Team Name', 'Rebounds']]
                team_rank_rebounds = season_games_details.groupby('TEAM_ID').sum().reset_index().sort_values('REB',
                                                                                                         ascending=False)
                team_rank_rebounds['Rank'] = range(1, len(team_rank_rebounds) + 1)
                selected_team_rank_rebounds = team_rank_rebounds[team_rank_rebounds['TEAM_ID'] == team_id][
                    ['TEAM_ID', 'REB', 'Rank']]
                selected_team_rebounds = selected_team_rank_rebounds.merge(df_team[['TEAM_ID', 'NICKNAME']],
                                                                           on='TEAM_ID').rename(
                    columns={'REB': 'Rebounds', 'NICKNAME': 'Team Name'})
                # Wins
                top_10_wins = season_games.groupby('HOME_TEAM_ID').apply(lambda x: x['HOME_TEAM_WINS'].sum()).nlargest(
                    10).reset_index(name='Wins')
                top_10_wins = top_10_wins.merge(df_team[['TEAM_ID', 'NICKNAME']], left_on='HOME_TEAM_ID',
                                                right_on='TEAM_ID')
                top_10_wins = top_10_wins.rename(columns={'NICKNAME': 'Team Name'})
                top_10_wins['Rank'] = top_10_wins.index + 1
                top_10_wins = top_10_wins[['Rank', 'Team Name', 'Wins']]
                team_rank_wins = season_games.groupby('HOME_TEAM_ID').apply(
                    lambda x: x['HOME_TEAM_WINS'].sum()).reset_index(name='Wins').sort_values('Wins', ascending=False)
                team_rank_wins['Rank'] = range(1, len(team_rank_wins) + 1)
                selected_team_rank_wins = team_rank_wins[team_rank_wins['HOME_TEAM_ID'] == team_id][
                    ['HOME_TEAM_ID', 'Wins', 'Rank']]
                selected_team_wins = selected_team_rank_wins.merge(df_team[['TEAM_ID', 'NICKNAME']],
                                                                   left_on='HOME_TEAM_ID', right_on='TEAM_ID').rename(
                    columns={'Wins': 'Wins', 'NICKNAME': 'Team Name'})
                st.subheader(f"Top 10 Teams by Points in {season}")
                st.table(top_10_points.set_index('Rank'))
                st.markdown(
                    f"**{team_name} Rank in Points:** {selected_team_rank_points['Rank'].values[0]} | **Points:** {selected_team_points['Points'].values[0]}")
                st.subheader(f"Top 10 Teams by Wins in {season}")
                st.table(top_10_wins.set_index('Rank'))
                st.markdown(
                    f"**{team_name} Rank in Wins:** {selected_team_rank_wins['Rank'].values[0]} | **Wins:** {selected_team_wins['Wins'].values[0]}")
                st.subheader(f"Top 10 Teams by Assists in {season}")
                st.table(top_10_assists.set_index('Rank'))
                st.markdown(
                    f"**{team_name} Rank in Assists:** {selected_team_rank_assists['Rank'].values[0]} | **Assists:** {selected_team_assists['Assists'].values[0]}")
                st.subheader(f"Top 10 Teams by Rebounds in {season}")
                st.table(top_10_rebounds.set_index('Rank'))
                st.markdown(
                    f"**{team_name} Rank in Rebounds:** {selected_team_rank_rebounds['Rank'].values[0]} | **Rebounds:** {selected_team_rebounds['Rebounds'].values[0]}")


elif selection == 'Player':
    player_list = df_players['PLAYER_NAME'].unique()
    selected_player = st.sidebar.selectbox('Select Player:', ['Select'] + list(player_list))
    if selected_player != 'Select':
        player_data = df_players[df_players['PLAYER_NAME'] == selected_player]
        player_id = player_data['PLAYER_ID'].values[0]
        section = st.sidebar.radio("Select Section:", ["General Info", "Match Details", "Rankings"])

        # General Info Section
        if section == 'General Info':
            st.header(f"Statistics for {selected_player}")
            team_id = player_data['TEAM_ID'].values[0]
            team_name = df_team[df_team['TEAM_ID'] == team_id]['NICKNAME'].values[0]
            st.markdown(f"**Team:** {team_name}")

            # Select year
            year = st.sidebar.slider('Select Year:', 2014, 2022, 2022)

            # Filter data based on the selected year
            player_year_games = df_games_details[(df_games_details['PLAYER_ID'] == player_id) & (df_games_details['SEASON'] == year)]

            # Calculate averages
            avg_points = player_year_games['PTS'].mean()
            avg_assists = player_year_games['AST'].mean()
            avg_rebounds = player_year_games['REB'].mean()

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Average Points:** {avg_points:.2f}")
                st.markdown(f"**Average Assists:** {avg_assists:.2f}")
            with col2:
                st.markdown(f"**Average Rebounds:** {avg_rebounds:.2f}")

            # Goals Percentage Pie Chart
            st.subheader(f"Scoring Methods in {year}")
            scoring_methods = ['FG3M', 'FGM', 'FTM']
            method_labels = ['Three Pointers', 'Field Goals', 'Free Throws']
            method_values = [player_year_games[method].sum() for method in scoring_methods]
            fig, ax = plt.subplots()
            ax.pie(method_values, labels=method_labels, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')
            st.pyplot(fig)

            # Points per Season Line Graph
            st.subheader(f"Total Points Scored in Each Season (2014-2022)")
            seasons = range(2014, 2023)
            total_points_per_season = []
            for s in seasons:
                season_points = df_games_details[(df_games_details['PLAYER_ID'] == player_id) & (df_games_details['SEASON'] == s)]['PTS'].sum()
                total_points_per_season.append(season_points)
            fig, ax = plt.subplots()
            ax.plot(seasons, total_points_per_season, marker='o', linestyle='-')
            ax.set_xlabel('Season')
            ax.set_ylabel('Total Points')
            ax.set_title(f'{selected_player} Total Points (2014-2022)')
            st.pyplot(fig)


        # Match Details Section
        elif section == "Match Details":
            st.header(f"Match Details for {selected_player}")

            # Select season
            season = st.sidebar.slider('Select Season:', 2014, 2022, 2022)

            # Filter data based on the selected season
            player_season_games = df_games_details[
                (df_games_details['PLAYER_ID'] == player_id) & (df_games_details['SEASON'] == season)]

            if not player_season_games.empty:
                # Join with df_games to get the necessary columns
                player_season_games = player_season_games.merge(df_games[['GAME_ID', 'GAME_DATE_EST', 'HOME_TEAM_ID',
                                                                          'VISITOR_TEAM_ID', 'PTS_home', 'PTS_away',
                                                                          'HOME_TEAM_WINS']], on='GAME_ID')

                player_season_games['DATE'] = pd.to_datetime(player_season_games['GAME_DATE_EST'])
                player_season_games.sort_values('DATE', inplace=True)
                player_season_games['RESULT'] = player_season_games.apply(
                    lambda row: 'Win' if (row['HOME_TEAM_ID'] == row['TEAM_ID'] and row['HOME_TEAM_WINS'] == 1) or (
                            row['VISITOR_TEAM_ID'] == row['TEAM_ID'] and row['HOME_TEAM_WINS'] == 0) else 'Loss',
                    axis=1)

                player_season_games['TEAM_POINTS'] = player_season_games.apply(
                    lambda row: row['PTS_home'] if row['HOME_TEAM_ID'] == row['TEAM_ID'] else row['PTS_away'], axis=1)

                player_season_games['OPPONENT_POINTS'] = player_season_games.apply(
                    lambda row: row['PTS_away'] if row['HOME_TEAM_ID'] == row['TEAM_ID'] else row['PTS_home'], axis=1)

                player_season_games['OPPONENT_TEAM'] = player_season_games.apply(
                    lambda row: df_team[df_team['TEAM_ID'] == (
                        row['VISITOR_TEAM_ID'] if row['HOME_TEAM_ID'] == row['TEAM_ID'] else row['HOME_TEAM_ID'])][
                                    'NICKNAME'].values[0] +
                                " (" + df_team[df_team['TEAM_ID'] == (
                        row['VISITOR_TEAM_ID'] if row['HOME_TEAM_ID'] == row['TEAM_ID'] else row['HOME_TEAM_ID'])][
                                    'ABBREVIATION'].values[0] + ")", axis=1)

                st.header("**Match Details:**")

                matches_to_show = 3

                # Line graph of matches
                plt.figure(figsize=(10, 6))
                plt.plot(player_season_games['DATE'], player_season_games['PTS'], marker='o', label='Player Points')
                for i, row in player_season_games.iterrows():
                    plt.text(row['DATE'], row['PTS'], row['RESULT'], fontsize=8, ha='right')
                plt.xlabel('Date (Day-Month)')
                plt.ylabel('Points')
                plt.title(f'{selected_player} Match Points Over Time')
                plt.legend()
                st.pyplot(plt)

                if 'match_count' not in st.session_state:
                    st.session_state.match_count = matches_to_show

                for index, row in player_season_games.iloc[:st.session_state.match_count].iterrows():
                    team_id = row['TEAM_ID']
                    team_name = df_team[df_team['TEAM_ID'] == team_id]['NICKNAME'].values[0]
                    opponent_team_id = row['HOME_TEAM_ID'] if row['TEAM_ID'] != row['HOME_TEAM_ID'] else row[
                        'VISITOR_TEAM_ID']
                    opponent_team = df_team[df_team['TEAM_ID'] == opponent_team_id]['NICKNAME'].values[0]
                    st.markdown(f"### {row['DATE'].strftime('%Y-%m-%d')}")
                    st.markdown(f"**Team:** {team_name} vs **Opponent Team:** {opponent_team}")
                    st.markdown(
                        f"**Team Points:** {row['TEAM_POINTS']} | **Opponent Points:** {row['OPPONENT_POINTS']}")
                    st.markdown(f"**Player Points:** {row['PTS']}")

                    # Points Breakdown
                    st.markdown("#### Points Breakdown")
                    points_breakdown = {
                        "Free Throws": row['FTM'] if not pd.isna(row['FTM']) else 0,
                        "Field Goals": row['FGM'] if not pd.isna(row['FGM']) else 0,
                        "Three Pointers": row['FG3M'] if not pd.isna(row['FG3M']) else 0,
                    }
                    points_breakdown_df = pd.DataFrame(points_breakdown.items(), columns=['Type', 'Value'])
                    st.table(points_breakdown_df)

                    st.markdown("---")

                if st.session_state.match_count < len(player_season_games):
                    if st.button('Load More'):
                        st.session_state.match_count += 5

        # Rankings Section
        elif section == "Rankings":
            st.header("Top 10 Players Rankings")

            # Select season
            season = st.sidebar.slider('Select Season:', 2014, 2022, 2022)

            # Filter data based on the selected season
            season_games_details = df_games_details[df_games_details['SEASON'] == season]

            # Group by PLAYER_ID and sum the statistics to avoid duplicate entries
            season_games_aggregated = season_games_details.groupby('PLAYER_ID', as_index=False).sum()

            # Points
            top_10_points = season_games_aggregated.nlargest(10, 'PTS')[['PLAYER_ID', 'PTS']]
            top_10_points = top_10_points.merge(df_players[['PLAYER_ID', 'PLAYER_NAME']],
                                                on='PLAYER_ID').drop_duplicates(subset=['PLAYER_ID'])
            top_10_points = top_10_points.rename(columns={'PTS': 'Points', 'PLAYER_NAME': 'Player Name'})
            top_10_points = top_10_points.sort_values(by='Points', ascending=False).reset_index(drop=True)
            top_10_points['Rank'] = top_10_points.index + 1
            top_10_points = top_10_points[['Rank', 'Player Name', 'Points']]

            player_rank_points = season_games_aggregated.sort_values('PTS', ascending=False).reset_index(drop=True)
            player_rank_points['Rank'] = player_rank_points.index + 1
            selected_player_rank_points = player_rank_points[player_rank_points['PLAYER_ID'] == player_id][
                ['PLAYER_ID', 'PTS', 'Rank']]
            selected_player_points = selected_player_rank_points.merge(df_players[['PLAYER_ID', 'PLAYER_NAME']],
                                                                       on='PLAYER_ID').rename(
                columns={'PTS': 'Points', 'PLAYER_NAME': 'Player Name'})

            st.subheader(f"Top 10 Players by Points in {season}")
            st.table(top_10_points.set_index('Rank'))

            st.markdown(
                f"**{selected_player} Rank in Points:** {selected_player_rank_points['Rank'].values[0]} | **Points:** {selected_player_points['Points'].values[0]}")

            # Assists
            top_10_assists = season_games_aggregated.nlargest(10, 'AST')[['PLAYER_ID', 'AST']]
            top_10_assists = top_10_assists.merge(df_players[['PLAYER_ID', 'PLAYER_NAME']],
                                                  on='PLAYER_ID').drop_duplicates(subset=['PLAYER_ID'])
            top_10_assists = top_10_assists.rename(columns={'AST': 'Assists', 'PLAYER_NAME': 'Player Name'})
            top_10_assists = top_10_assists.sort_values(by='Assists', ascending=False).reset_index(drop=True)
            top_10_assists['Rank'] = top_10_assists.index + 1
            top_10_assists = top_10_assists[['Rank', 'Player Name', 'Assists']]

            player_rank_assists = season_games_aggregated.sort_values('AST', ascending=False).reset_index(drop=True)
            player_rank_assists['Rank'] = player_rank_assists.index + 1
            selected_player_rank_assists = player_rank_assists[player_rank_assists['PLAYER_ID'] == player_id][
                ['PLAYER_ID', 'AST', 'Rank']]
            selected_player_assists = selected_player_rank_assists.merge(df_players[['PLAYER_ID', 'PLAYER_NAME']],
                                                                         on='PLAYER_ID').rename(
                columns={'AST': 'Assists', 'PLAYER_NAME': 'Player Name'})

            st.subheader(f"Top 10 Players by Assists in {season}")
            st.table(top_10_assists.set_index('Rank'))

            st.markdown(
                f"**{selected_player} Rank in Assists:** {selected_player_rank_assists['Rank'].values[0]} | **Assists:** {selected_player_assists['Assists'].values[0]}")

            # Rebounds
            top_10_rebounds = season_games_aggregated.nlargest(10, 'REB')[['PLAYER_ID', 'REB']]
            top_10_rebounds = top_10_rebounds.merge(df_players[['PLAYER_ID', 'PLAYER_NAME']],
                                                    on='PLAYER_ID').drop_duplicates(subset=['PLAYER_ID'])
            top_10_rebounds = top_10_rebounds.rename(columns={'REB': 'Rebounds', 'PLAYER_NAME': 'Player Name'})
            top_10_rebounds = top_10_rebounds.sort_values(by='Rebounds', ascending=False).reset_index(drop=True)
            top_10_rebounds['Rank'] = top_10_rebounds.index + 1
            top_10_rebounds = top_10_rebounds[['Rank', 'Player Name', 'Rebounds']]

            player_rank_rebounds = season_games_aggregated.sort_values('REB', ascending=False).reset_index(drop=True)
            player_rank_rebounds['Rank'] = player_rank_rebounds.index + 1
            selected_player_rank_rebounds = player_rank_rebounds[player_rank_rebounds['PLAYER_ID'] == player_id][
                ['PLAYER_ID', 'REB', 'Rank']]
            selected_player_rebounds = selected_player_rank_rebounds.merge(df_players[['PLAYER_ID', 'PLAYER_NAME']],
                                                                           on='PLAYER_ID').rename(
                columns={'REB': 'Rebounds', 'PLAYER_NAME': 'Player Name'})

            st.subheader(f"Top 10 Players by Rebounds in {season}")
            st.table(top_10_rebounds.set_index('Rank'))

            st.markdown(
                f"**{selected_player} Rank in Rebounds:** {selected_player_rank_rebounds['Rank'].values[0]} | **Rebounds:** {selected_player_rebounds['Rebounds'].values[0]}")
