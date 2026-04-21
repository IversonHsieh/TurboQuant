import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import beta
from scipy.special import gamma

# 設置現代化科技感配色方案（深色模式友好）
# 使用科技藍、青色、紫色、橙色等現代配色
plt.rcParams['figure.facecolor'] = '#1a1a2e'  # 深藍背景
plt.rcParams['axes.facecolor'] = '#16213e'    # 稍淺的藍色
plt.rcParams['axes.edgecolor'] = '#0f3460'    # 邊框顏色
plt.rcParams['axes.labelcolor'] = '#e8e8e8'   # 標籤顏色
plt.rcParams['xtick.color'] = '#a0a0a0'       # x 軸刻度顏色
plt.rcParams['ytick.color'] = '#a0a0a0'       # y 軸刻度顏色
plt.rcParams['text.color'] = '#e8e8e8'        # 文字顏色
plt.rcParams['grid.color'] = '#0f3460'        # 網格顏色
plt.rcParams['axes.linewidth'] = 1.5          # 軸線寬度
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11

# 現代科技感配色
COLORS = {
    'cyan': '#00d9ff',      # 青色 - 主要強調色
    'blue': '#4a9eff',      # 藍色 - 次要色
    'purple': '#a855f7',    # 紫色 - 強調色
    'orange': '#ff7e33',    # 橙色 - 對比色
    'green': '#00ff88',     # 綠色 - 成功色
    'pink': '#ff3385',      # 粉紅色 - 點綴色
    'yellow': '#ffe633',    # 黃色 - 警告色
    'red': '#ff4757',       # 紅色 - 錯誤色
}

# 創建 x 軸數據 (Beta distribution 的範圍是 [0, 1])
x = np.linspace(0, 1, 1000)

# 創建 figure 和 axis - 使用更大的尺寸和現代化設計
fig = plt.figure(figsize=(16, 12))
fig.patch.set_facecolor('#1a1a2e')

# 添加主標題
fig.suptitle('Beta Distribution (Beta 分佈)', fontsize=24, fontweight='bold', 
             color='#e8e8e8', y=0.98)

# 創建 2x2 的子圖佈局
ax1 = fig.add_subplot(2, 2, 1)
ax2 = fig.add_subplot(2, 2, 2)
ax3 = fig.add_subplot(2, 2, 3)
ax4 = fig.add_subplot(2, 2, 4)

# 設置所有子圖的背景色
for ax in [ax1, ax2, ax3, ax4]:
    ax.set_facecolor('#16213e')
    ax.spines['bottom'].set_color('#0f3460')
    ax.spines['top'].set_color('#0f3460')
    ax.spines['left'].set_color('#0f3460')
    ax.spines['right'].set_color('#0f3460')
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['top'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['right'].set_linewidth(1.5)

# ========== 左上圖：不同參數的 Beta distribution ==========
params1 = [
    (0.5, 0.5, 'U-shaped', COLORS['pink']),
    (1, 1, 'Uniform', COLORS['cyan']),
    (2, 5, 'Right-skewed', COLORS['blue']),
    (5, 2, 'Left-skewed', COLORS['purple']),
]

for alpha, beta_param, label, color in params1:
    y = beta.pdf(x, alpha, beta_param)
    # 限制 y 軸範圍避免無限值
    y = np.clip(y, 0, 10)
    ax1.plot(x, y, linewidth=2.5, color=color, label=label, alpha=0.9)
    # 添加填充效果
    ax1.fill_between(x, 0, y, alpha=0.15, color=color)

ax1.set_xlabel('x', fontsize=13, color='#a0a0a0')
ax1.set_ylabel('Probability Density\n(機率密度)', fontsize=13, color='#a0a0a0')
ax1.set_title('Beta Distribution - Various Parameters I\n(各種參數形狀 I)', 
               fontsize=15, fontweight='bold', color='#e8e8e8', pad=15)
ax1.legend(loc='upper right', fontsize=10, framealpha=0.1, facecolor='#1a1a2e', 
           edgecolor='#0f3460', labelcolor='#e8e8e8')
ax1.grid(True, alpha=0.2, linestyle='--', linewidth=0.8)
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 3.5)

# ========== 右上圖：更多參數組合 ==========
params2 = [
    (2, 2, 'Symmetric', COLORS['green']),
    (5, 5, 'Peaked', COLORS['orange']),
    (0.5, 1, 'J-shaped', COLORS['red']),
    (1, 0.5, 'Reverse J', COLORS['yellow']),
]

for alpha, beta_param, label, color in params2:
    y = beta.pdf(x, alpha, beta_param)
    y = np.clip(y, 0, 10)
    ax2.plot(x, y, linewidth=2.5, color=color, label=label, alpha=0.9)
    ax2.fill_between(x, 0, y, alpha=0.15, color=color)

ax2.set_xlabel('x', fontsize=13, color='#a0a0a0')
ax2.set_ylabel('Probability Density\n(機率密度)', fontsize=13, color='#a0a0a0')
ax2.set_title('Beta Distribution - Various Parameters II\n(各種參數形狀 II)', 
               fontsize=15, fontweight='bold', color='#e8e8e8', pad=15)
ax2.legend(loc='upper right', fontsize=10, framealpha=0.1, facecolor='#1a1a2e',
           edgecolor='#0f3460', labelcolor='#e8e8e8')
ax2.grid(True, alpha=0.2, linestyle='--', linewidth=0.8)
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 3.5)

# ========== 左下圖：TurboQuant 中的 Beta distribution ==========
def turboquant_beta_pdf(x, d):
    """TurboQuant 中使用的 Beta distribution PDF"""
    coeff = gamma(d/2) / (np.sqrt(np.pi) * gamma((d-1)/2))
    return coeff * np.power(np.maximum(1 - x**2, 0), (d-3)/2)

x_tq = np.linspace(-1, 1, 1000)
dimensions = [3, 5, 10, 50, 100]
tq_colors = [COLORS['pink'], COLORS['orange'], COLORS['cyan'], COLORS['blue'], COLORS['purple']]

for d, color in zip(dimensions, tq_colors):
    y = turboquant_beta_pdf(x_tq, d)
    ax3.plot(x_tq, y, linewidth=2.5, color=color, label=f'd={d}', alpha=0.9)
    ax3.fill_between(x_tq, 0, y, alpha=0.15, color=color)

ax3.set_xlabel('x', fontsize=13, color='#a0a0a0')
ax3.set_ylabel('Probability Density\n(機率密度)', fontsize=13, color='#a0a0a0')
ax3.set_title('Beta Distribution in TurboQuant\n(高維度收斂特性)', 
              fontsize=15, fontweight='bold', color='#e8e8e8', pad=15)
ax3.legend(loc='upper center', fontsize=10, framealpha=0.1, facecolor='#1a1a2e',
           edgecolor='#0f3460', labelcolor='#e8e8e8', ncol=5)
ax3.grid(True, alpha=0.2, linestyle='--', linewidth=0.8)
ax3.set_xlim(-1, 1)

# 添加註解說明高維度收斂
max_y = max(turboquant_beta_pdf(x_tq, 100))
ax3.annotate('Converges to N(0, 1/d)\n(收斂到常態分佈)', 
             xy=(0, turboquant_beta_pdf(0, 100)), 
             xytext=(0.35, max_y*0.75),
             fontsize=11, color='#00ff88',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a2e', 
                       edgecolor='#00ff88', linewidth=1.5, alpha=0.8),
             arrowprops=dict(arrowstyle='->', color='#00ff88', linewidth=2))

# ========== 右下圖：均值和變異數的變化 ==========
alphas = np.linspace(0.5, 10, 100)
betas = alphas  # 對稱情況

means = alphas / (alphas + betas)
variances = (alphas * betas) / ((alphas + betas)**2 * (alphas + betas + 1))

# 主軸 - 均值
line1, = ax4.plot(alphas, means, linewidth=3, color=COLORS['cyan'], label='Mean (均值)')
ax4.fill_between(alphas, 0, means, alpha=0.2, color=COLORS['cyan'])

# 次軸 - 變異數
ax4_twin = ax4.twinx()
ax4_twin.spines['bottom'].set_color('#0f3460')
ax4_twin.spines['top'].set_color('#0f3460')
ax4_twin.spines['left'].set_color('#0f3460')
ax4_twin.spines['right'].set_color('#0f3460')
ax4_twin.set_facecolor('#16213e')
ax4_twin.tick_params(colors='#a0a0a0')

line2, = ax4_twin.plot(alphas, variances, linewidth=3, color=COLORS['orange'], 
                       label='Variance (變異數)')
ax4_twin.fill_between(alphas, 0, variances, alpha=0.2, color=COLORS['orange'])

ax4.set_xlabel('α = β (Symmetric Parameters / 對稱參數)', fontsize=13, color='#a0a0a0')
ax4.set_ylabel('Mean (均值)', color=COLORS['cyan'], fontsize=13, fontweight='bold')
ax4_twin.set_ylabel('Variance (變異數)', color=COLORS['orange'], fontsize=13, fontweight='bold')
ax4.set_title('Mean and Variance vs Parameters\n(均值和變異數 vs 參數)', 
              fontsize=15, fontweight='bold', color='#e8e8e8', pad=15)

# 合併圖例
lines = [line1, line2]
labels = ['Mean (均值)', 'Variance (變異數)']
ax4.legend(lines, labels, loc='upper right', fontsize=11, framealpha=0.1, 
           facecolor='#1a1a2e', edgecolor='#0f3460', labelcolor='#e8e8e8')

ax4.grid(True, alpha=0.2, linestyle='--', linewidth=0.8)
ax4.set_ylim(0, 1.1)
ax4_twin.set_ylim(0, 0.06)

# 添加網格線到雙 y 軸
ax4_twin.grid(False)

plt.tight_layout(rect=[0, 0.02, 1, 0.96])

# 添加底部說明文字
fig.text(0.5, 0.01, 
         'Beta distribution is used in TurboQuant to model coordinate distributions after random rotation.\n'
         'TurboQuant 使用 Beta 分佈來建模隨機旋轉後的座標分佈。',
         fontsize=10, color='#808080', ha='center', style='italic')

# 保存為 SVG（確保文字正確編碼）
plt.savefig('docs/svg/beta_distribution.svg', format='svg', bbox_inches='tight', 
            facecolor=fig.get_facecolor(), edgecolor='none')
# 同時保存 PNG 預覽
plt.savefig('docs/svg/beta_distribution.png', format='png', dpi=150, 
            bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')

print("SVG 和 PNG 圖表已生成完成！")
print("- docs/svg/beta_distribution.svg")
print("- docs/svg/beta_distribution.png")
print("\n配色方案：深色模式友好的科技感設計")
print("- 背景：深藍色 (#1a1a2e)")
print("- 強調色：青色 (#00d9ff)、藍色 (#4a9eff)、紫色 (#a855f7)")
print("- 對比色：橙色 (#ff7e33)、綠色 (#00ff88)")
