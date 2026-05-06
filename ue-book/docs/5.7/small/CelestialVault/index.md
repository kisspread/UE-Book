# CelestialVault

> A DaySequence implementation of a Celestial Vault for Earth using ephemeris

| 属性 | 值 |
|---|---|
| 中文名 | 天穹天象 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（DaySequence 资产、蓝图预设） |
| 模块 | `CelestialVault` (Runtime), `CelestialVaultEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CelestialVault) | |

## 总体用途

CelestialVault 是一个基于 DaySequence 系统的插件，用于真实模拟地球天空的天象（太阳位置、月相、大气散射等）。它利用星历表（ephemeris）精确计算太阳和月球的运行轨迹，并自动控制场景中的光照（太阳方向灯）、指数高度雾和全局后处理体积，从而在引擎内还原任意地理坐标下的真实户外环境。

该插件解决了传统静态天空盒无法匹配动态时间、无法表现月相等天文现象的问题，适合需要**真实时间驱动**的户外场景。

## 模块列表

| 模块 | 类型 | 一句话总结 | 子文档 |
|---|---|---|---|
| `CelestialVault` | Runtime | 核心运行时：计算太阳/月球位置、光照方向、月相，并驱动 DaySequence | [CelestialVault.md](./CelestialVault.md) |
| `CelestialVaultEditor` | Runtime | 编辑器扩展：提供 CelestialVault 蓝图节点、Actor 配置界面及调试工具 | [CelestialVaultEditor.md](./CelestialVaultEditor.md) |

## 使用场景

- 模拟真实地球光照的开放世界游戏（如野外生存、冒险游戏）
- 军事/航空航天视景仿真（需要精确太阳方位角）
- 电影预演或虚拟制片中快速匹配真实拍摄地的时间与天象
- 天文学教育或天文馆可视化项目
- 任何需要动态天空、日出日落、月相变化的户外体验

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CelestialVault)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CelestialVault/Tests)（位于插件内）