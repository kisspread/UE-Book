# Audio Properties

> Allows to define arbitrary derivable sets of properties to be injected in any audio asset

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产/配置） |
| 模块 | `AudioProperties` (Editor), `AudioPropertiesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AudioProperties) | |

## 用途

该插件旨在为 Unreal Engine 的音频系统提供一套可扩展的属性框架。它允许开发者定义任意的、可继承的属性集合，并将这些属性“注入”到任何音频资产（如 Sound Wave、Sound Cue 等）中。这解决了音频资产缺乏统一、结构化元数据或运行时参数接口的问题，使得音频资产的属性可以像其他资产类型一样被灵活地定义、查询和修改。

## 使用场景

- 你需要为游戏中的所有音频资产统一添加“情绪标签”、“环境区域”或“优先级”等自定义属性，并在运行时根据这些属性进行筛选或混合。
- 你正在开发一个音频中间件或工具链，需要一种标准化的方式来为音频资产附加额外的配置数据。
- 你希望音频设计师能够在编辑器中通过统一的界面为不同音频资产设置和管理一组共享的、可派生的参数。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `AudioProperties` | Editor | 核心运行时模块，定义音频属性的数据结构、资产注入逻辑和运行时访问接口。 |
| `AudioPropertiesEditor` | Editor | 编辑器扩展模块，提供用于创建、编辑和管理音频属性集的用户界面和资产编辑器。 |

*详细的 API 用法和示例，请参阅各模块的独立文档：*
- [AudioProperties 模块文档](AudioProperties.md)
- [AudioPropertiesEditor 模块文档](AudioPropertiesEditor.md)

### 近期更新

- 2026-04-14 `01c9ce5d` [ContentBrowser] New Add Menu Audio Menu
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-02-12 `68131ef1` Instantiate Audio Properties Name Parser when creating new Property Sheet, as this is the de facto d
- 2026-01-15 `738ab46a` Fixed localization warnings
- 2026-01-14 `4b3fba09` Walk UClass inheritance when overriding property details from a property sheet to avoid visualizatio

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AudioProperties)
- [官方文档]()（暂无）
- [测试用例]()（暂无）