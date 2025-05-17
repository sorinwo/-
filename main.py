
import discord
from discord.ext import commands
from discord import app_commands

# Set up bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Global variables
current_robux = 0
current_won = 0
ADMIN_ID = ADMIN_ID  # Admin's Discord ID
calculator_message = None  # Store the calculator message

@bot.tree.command(name="버튼생성", description="계산기 버튼을 생성합니다")
async def create_price_buttons(interaction: discord.Interaction):
    # Check if the user is the admin
    if interaction.user.id != ADMIN_ID:
        await interaction.response.send_message("이 명령어는 관리자만 사용할 수 있습니다.")
        return
        
    # Create buttons
    view = discord.ui.View()
    
    # Create buttons with conversion labels
    won_to_robux = discord.ui.Button(label="원 → 로벅 계산", style=discord.ButtonStyle.gray)
    robux_to_won = discord.ui.Button(label="로벅 → 원 계산", style=discord.ButtonStyle.gray)
    
    # Add button callbacks
    async def won_to_robux_callback(button_interaction):
        try:
            # Create modal for won input
            modal = discord.ui.Modal(title="원 → 로벅 계산")
            won_input = discord.ui.TextInput(
                label="계산할 원화 금액을 입력하세요",
                placeholder="숫자만 입력해주세요",
                required=True
            )
            modal.add_item(won_input)

            async def modal_submit(modal_interaction):
                try:
                    won_amount = int(won_input.value)
                    robux_amount = int((won_amount / current_won) * current_robux)
                    embed = discord.Embed(title=" 계산 결과", color=0x808080)
                    embed.add_field(name="", value=f"```{won_amount:,}원 ➜ {robux_amount:,}로벅```", inline=False)
                    await modal_interaction.response.send_message(embed=embed, ephemeral=True)
                except:
                    await modal_interaction.response.send_message("올바른 금액을 입력해주세요.", ephemeral=True)

            modal.on_submit = modal_submit
            await button_interaction.response.send_modal(modal)
        except:
            await button_interaction.response.send_message("계산 중 오류가 발생했습니다.", ephemeral=True)
    
    async def robux_to_won_callback(button_interaction):
        try:
            # Create modal for robux input
            modal = discord.ui.Modal(title="로벅 → 원 계산")
            robux_input = discord.ui.TextInput(
                label="계산할 로벅스 금액을 입력하세요",
                placeholder="숫자만 입력해주세요",
                required=True
            )
            modal.add_item(robux_input)

            async def modal_submit(modal_interaction):
                try:
                    robux_amount = int(robux_input.value)
                    won_amount = int((robux_amount / current_robux) * current_won)
                    embed = discord.Embed(title=" 계산 결과", color=0x808080)
                    embed.add_field(name="", value=f"```{robux_amount:,}로벅 ➜ {won_amount:,}원```", inline=False)
                    await modal_interaction.response.send_message(embed=embed, ephemeral=True)
                except:
                    await modal_interaction.response.send_message("올바른 금액을 입력해주세요.", ephemeral=True)

            modal.on_submit = modal_submit
            await button_interaction.response.send_modal(modal)
        except:
            await button_interaction.response.send_message("계산 중 오류가 발생했습니다.", ephemeral=True)
    
    won_to_robux.callback = won_to_robux_callback
    robux_to_won.callback = robux_to_won_callback
    
    view.add_item(won_to_robux)
    view.add_item(robux_to_won)
    
    # Send message with current price and buttons
    try:
        global calculator_message
        embed = discord.Embed(title="🧮 계산기", color=0x808080)
        embed.add_field(name="현재 비율", value=f"```{current_robux:,}로벅 = {current_won:,}원```", inline=False)
        embed.set_footer(text="원하시는 계산 버튼을 클릭해주세요")
        message = await interaction.channel.send(embed=embed, view=view)
        calculator_message = message
        await interaction.response.send_message("계산기가 생성되었습니다.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("버튼 생성 중 오류가 발생했습니다.")

@bot.tree.command(name="가격설정", description="계산 기준 가격을 설정합니다")
@app_commands.describe(robux="로벅스 갯수", price="설정할 가격 (원)")
async def set_price(interaction: discord.Interaction, robux: int, price: int):
    # Check if the user is the admin
    if interaction.user.id != ADMIN_ID:
        await interaction.response.send_message("이 명령어는 관리자만 사용할 수 있습니다.")
        return
        
    # If user is admin, proceed with price setting logic
    try:
        global current_robux, current_won, calculator_message
        current_robux = robux
        current_won = price
        embed = discord.Embed(title="✅ 비율 설정 완료", color=0x808080)
        embed.add_field(name="", value=f"```{robux:,}로벅 = {price:,}원```", inline=False)
        await interaction.response.send_message(embed=embed)
        
        # Update calculator message if it exists
        if calculator_message:
            calculator_embed = discord.Embed(title="🧮 계산기", color=0x808080)
            calculator_embed.add_field(name="현재 비율", value=f"```{current_robux:,}로벅 = {current_won:,}원```", inline=False)
            calculator_embed.set_footer(text="원하시는 계산 버튼을 클릭해주세요")
            try:
                await calculator_message.edit(embed=calculator_embed)
            except discord.NotFound:
                calculator_message = None
    except Exception as e:
        await interaction.response.send_message("가격 설정 중 오류가 발생했습니다.")

@bot.event
async def on_ready():
    print(f'봇이 성공적으로 실행되었습니다: {bot.user.name}')
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"슬래시 명령어 동기화 중 오류 발생: {e}")

# Run the bot
bot.run('BOT.TOKEN')