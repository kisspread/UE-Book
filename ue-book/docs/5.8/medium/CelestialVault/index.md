# Celestial Vault

> A DaySequence implementation of a Celestial Vault for Earth using ephemeris

| 属性 | 值 |
|---|---|
| 中文名 | 天穹模拟 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（天穹蓝图资产） |
| 模块 | `CelestialVault` (Runtime), `CelestialVaultEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CelestialVault) | |

## 用途

基于天文星历（ephemeris）数据，在 UE5 中模拟真实的地球天穹（Celestial Vault）。通过 DaySequence 系统驱动太阳、月亮、星空等天体的运行，提供符合真实天文规律的昼夜循环和天体位置计算。

该插件解决的核心问题是：**在虚拟场景中以天文学精度还原地球天空的真实变化**——包括基于地理位置和时间计算日月升落、恒星视差补偿、深空天体跟随观察者等。

## 使用场景

- 你需要一个基于真实天文数据的昼夜循环系统，而不是简单的 Day/Night 动画
- 你在做建筑可视化或仿真项目，需要精确模拟特定地理位置和时间的天空状态
- 你需要天空中的恒星、太阳、月亮位置与现实一致，用于天文教育或 VR 体验
- 你需要自定义观察者的经纬度坐标（Topocentric）来计算本地天体视角

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`CelestialVault`](CelestialVault.md) | Runtime | 核心天穹模拟引擎，包含星历计算、天体轨道、Topocentric 观测系统 |
| [`CelestialVaultEditor`](CelestialVaultEditor.md) | Runtime | 编辑器辅助功能，提供天穹组件的编辑器内可视化与配置支持 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CelestialVault)
- [CelestialVault 模块文档](CelestialVault.md)
- [CelestialVaultEditor 模块文档](CelestialVaultEditor.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-04-30 | `8701bcf1` | Fix TopocentricVaultComponent attachment to use NorthOffsetComponent as parent | 修复 TopocentricVaultComponent 以 NorthOffsetComponent 为父节点的挂载逻辑 |
| 2026-04-29 | `b69b383a` | Fixed: The DeepSky now follows the observer to remove the parallax effect on Stars | 深空天体现在跟随观察者移动，消除恒星视差效果 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-04-10 | `8130162b` | Switched the Celestial Vault Plugin to Beta | 将天穹插件切换为 Beta 状态 |

### 维护评价

该插件非常新（约 1 个月），目前处于 **Beta 阶段**，正处于密集开发期。最近一个月内有 5 次提交，涵盖组件挂载修复、视差修正、编译警告清理等实质性改动，维护活跃度高。

⚠️ **注意**：`IsBetaVersion=true`，API 可能发生变动，不建议在生产环境直接依赖。适合实验和原型开发阶段使用。