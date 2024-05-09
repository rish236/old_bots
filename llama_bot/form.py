import discord
from datetime import datetime
import csv

class Form(discord.ui.View):
    def __init__(self, interaction: discord.Interaction) -> None:
        super().__init__(timeout=None)
        self.interaction = interaction

    @discord.ui.button(label="Fill Form", style=discord.ButtonStyle.green, custom_id="form_button")
    async def form_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FormFillout())


class FormFillout(discord.ui.Modal, title="Form"):

    token = discord.ui.TextInput(label="Token Name", style=discord.TextStyle.short, placeholder="BloodLoop (case insensitive)", required=True)
    wallet = discord.ui.TextInput(label="Your Wallet Address", style=discord.TextStyle.short, placeholder="0x..", required=True)
    link = discord.ui.TextInput(label="Etherscan Link", style=discord.TextStyle.short, placeholder="https://etherscan.io/..", required=True)
    amount = discord.ui.TextInput(label="Amount", style=discord.TextStyle.short, placeholder="$500.00", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        description = discord.Embed(
            description=f"Wallet Address: \n{self.wallet.value} \nEtherscan Link: \n{self.link.value}\nTime Wanted: \n{self.amount.value}",
            color=0xffffff
        )
        name  = interaction.user.name
        user_id = interaction.user.id

        
        formatted_date = datetime.utcnow().strftime("%A, %B %d, %Y %I:%M %p")
        data = [formatted_date,self.token.value.lower(),user_id, self.wallet.value, self.link.value, self.amount.value]
        with open("form.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)

        await interaction.response.send_message(f'Thanks for filling out the form, {name}!', ephemeral=True)