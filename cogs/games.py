import os
import sys
import json
import discord
import asyncio
from discord import app_commands, Interaction, TextChannel, Embed
from discord.ext import commands, tasks
from discord.app_commands import Choice
from datetime import datetime, timedelta
from helpers import *
import time
import uuid

def generate_unique_reminder_id():
    """Generate a unique reminder ID using UUID."""
    return uuid.uuid4().hex.replace("-", "")  # Generate a random unique ID

class Games(commands.Cog):
    group = app_commands.Group(name="games", description="Game Commands")

    def __init__(self, bot):
        self.bot = bot

    @group.command(name="tictactoe", description="Play Tic Tac Toe with a friend.")
    async def tictactoe(self, interaction: Interaction, player1: discord.User, player2: discord.User):
        """Starts a Tic Tac Toe game between two players."""
        # Invite player2 to join the game
        await interaction.response.defer()

        await self.invite_player2(interaction, player2)

        # Initialize the game with both players
        game = TicTacToe(player1.name, player2.name)
        
        # Start the game loop
        current_player = player1
        while not game.is_over:
            # Ask the current player to make a move
            await self.turn(interaction, current_player, game)
            
            # Switch to the other player
            current_player = player2 if current_player == player1 else player1

        # Declare the winner
        winner = game.get_winner()
        if winner:
            await interaction.followup.send_message(f"{winner} wins!")
        else:
            await interaction.followup.send_message("It's a tie!")

    async def invite_player2(self, interaction: Interaction, player2: discord.User):
        """Invite the second player to the game."""
        await interaction.followup.send_message(f"{player2.mention}, you've been invited to play Tic Tac Toe!")
    
    async def turn(self, interaction: Interaction, current_player: discord.User, game: 'TicTacToe'):
        """Handle the current player's turn."""
        # Simulate asking the player to make a move
        await interaction.followup.send_message(f"{current_player.mention}, it's your turn! Please pick a spot (1-9).")
        
        # Here you'd wait for the player's input, but for now we'll simulate it
        move = await self.get_player_move(interaction, current_player)
        
        # Apply the move to the game
        game.make_move(current_player.name, move)

    async def get_player_move(self, interaction: Interaction, player: discord.User):
        """Get the player's move. For now, we're simulating this with a random move."""
        # Simulate the player picking a move (this should be replaced with actual player input handling)
        await interaction.followup.send_message(f"{player.mention}, your move is being simulated.")
        return 1  # Replace with actual logic for getting the player's input


class TicTacToe:
    def __init__(self, player1: str, player2: str):
        self.board = [None] * 9  # 3x3 board as a flat list
        self.player1 = player1
        self.player2 = player2
        self.is_over = False
        self.winner = None

    def make_move(self, player: str, position: int):
        """Make a move on the board."""
        if self.board[position - 1] is None:
            self.board[position - 1] = player
            self.check_game_over()

    def check_game_over(self):
        """Check if the game is over and set the winner if there is one."""
        winning_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
            (0, 4, 8), (2, 4, 6)              # Diagonals
        ]
        for a, b, c in winning_combinations:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] is not None:
                self.is_over = True
                self.winner = self.board[a]
                return

        if all(self.board):  # If all positions are filled
            self.is_over = True

    def get_winner(self):
        """Return the winner's name, or None if it's a tie."""
        return self.winner


async def setup(bot):
    await bot.add_cog(Games(bot))
    # await bot.tree.add_command(Games.group)
