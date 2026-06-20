import os
import json
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
DATA_FILE = "raids.json"


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class RaidView(discord.ui.View):
    def __init__(self, raid_name, date_time, max_members):
        super().__init__(timeout=None)

        self.raid_name = raid_name
        self.date_time = date_time
        self.max_members = max_members
        self.participants = []

    def create_embed(self):
        if self.participants:
            members_text = "\n".join(
                f"{i+1}. {name}"
                for i, name in enumerate(self.participants)
            )
        else:
            members_text = "なし"

        embed = discord.Embed(
            title="📢 レイド募集",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="募集名",
            value=self.raid_name,
            inline=False
        )

        embed.add_field(
            name="日時",
            value=self.date_time,
            inline=False
        )

        embed.add_field(
            name="募集人数",
            value=f"{len(self.participants)}/{self.max_members}",
            inline=False
        )

        embed.add_field(
            name="参加者",
            value=members_text,
            inline=False
        )

        return embed

    @discord.ui.button(
        label="参加",
        style=discord.ButtonStyle.green,
        custom_id="join_button"
    )
    async def join_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        user_name = interaction.user.display_name

        if user_name in self.participants:
            await interaction.response.send_message(
                "既に参加しています。",
                ephemeral=True
            )
            return

        if len(self.participants) >= self.max_members:
            await interaction.response.send_message(
                "満員です。",
                ephemeral=True
            )
            return

        self.participants.append(user_name)

        if len(self.participants) >= self.max_members:
            button.disabled = True
            button.label = "満員"

        await interaction.response.edit_message(
            embed=self.create_embed(),
            view=self
        )

    @discord.ui.button(
        label="キャンセル",
        style=discord.ButtonStyle.red,
        custom_id="cancel_button"
    )    
    async def cancel_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        user_name = interaction.user.display_name

        if user_name not in self.participants:
            await interaction.response.send_message(
                "参加していません。",
                ephemeral=True
            )
            return

        self.participants.remove(user_name)

        join_button = self.children[0]
        join_button.disabled = False
        join_button.label = "参加"

        await interaction.response.edit_message(
            embed=self.create_embed(),
            view=self
        )


@bot.tree.command(
    name="raid",
    description="レイド募集を作成"
)
@app_commands.describe(
    raid_name="募集名",
    date_time="日時",
    max_members="募集人数"
)
async def raid(
    interaction: discord.Interaction,
    raid_name: str,
    date_time: str,
    max_members: int
):

    view = RaidView(
        raid_name,
        date_time,
        max_members
    )

    await interaction.response.send_message(
        embed=view.create_embed(),
        view=view
    )


@bot.event
async def on_ready():

    bot.add_view(
        RaidView(
            "temp",
            "temp",
            999
        )
    )

    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)}個のコマンドを同期しました")
    except Exception as e:
        print(e)

    print(f"ログイン完了: {bot.user}")


bot.run(TOKEN)
