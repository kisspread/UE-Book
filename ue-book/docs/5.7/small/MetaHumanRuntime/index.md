# MetaHumanRuntime

> Deprecated plugin now redirected to MetaHumanSDK

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 运行时（已废弃） |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（废弃重定向） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetaHuman/MetaHumanRuntime) | |

## 用途

MetaHumanRuntime 是一个已废弃的插件，被 `MetaHumanSDK` 插件取代。它的唯一作用是提供从旧插件名称到新 `MetaHumanSDK` 插件的自动重定向，确保引用 `MetaHumanRuntime` 的旧项目仍能正常工作，无需手动修改插件引用。

插件本身不包含任何源代码、蓝图资产或功能代码。当启用时，它会自动加载并重定向到 `MetaHumanSDK` 及其对应的运行时模块 `MetaHumanSDKRuntime`。

## 使用场景

- **旧项目迁移**：如果你有一个使用 `MetaHumanRuntime` 插件的 UE 5.3–5.5 项目，在升级到 UE 5.7 时，此插件会自动将依赖重定向到 `MetaHumanSDK`，避免编译或加载错误。
- **向后兼容**：MetaHuman 功能已整合到 `MetaHumanSDK`，新项目应直接使用 `MetaHumanSDK`，无需再启用本插件。

## 蓝图用法

本插件不提供任何蓝图可调用函数或属性。无需使用。

## C++ 用法

本插件不提供任何 C++ 头文件或 API。如果需要 MetaHuman 运行时功能，应引用 `MetaHumanSDKRuntime` 模块。

### 头文件引入

```cpp
// 请使用 MetaHumanSDK 相关头文件，例如：
#include "MetaHumanSDKRuntime.h"
```

### 基本用法

无。

## Demo 示例

无独立示例。请参考 `MetaHumanSDK` 插件的相关文档和示例。

## 模块依赖

本插件没有自己的编译模块，也不产生任何依赖。使用旧项目时，如果原来依赖 `MetaHumanRuntime`，请确保同时启用了 `MetaHumanSDK` 插件。

## 维护状态

### 近期更新

```
- 2024-09-16 62f8cc0c 无法加载插件，缺少依赖 MetaHumanRuntime（修复重定向逻辑）
- 2024-08-19 79003ad1 将 MetaHumanRuntime 插件移动到 MetaHumanSDK 插件并重命名为 MetaHumanSDKRuntime
- 2024-08-08 ea519b5c [MH-12702] 播放带有优化 MetaHuman 的关卡后编辑器崩溃修复
- 2024-07-31 8e8004fd MetaHuman 组件在 UE 中的改进
- 2024-07-24 bd22b183 修复 body parts 控制绑定无法运行的问题
```

### 维护评价

该插件创建于 2024 年 7 月，属于实验性插件，但在同年 8 月已被整合并废弃。自 2024 年 9 月最后一次修复重定向 bug 后，没有进一步的功能更新。

**警告**：此插件已经废弃，不应在新项目中启用。Epic 官方强烈建议迁移至 `MetaHumanSDK` 插件。如果继续使用，未来引擎版本中可能被完全移除。推荐直接使用 `MetaHumanSDK` 以获得完整功能和更新支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetaHuman/MetaHumanRuntime)
- [官方文档 - MetaHuman SDK](https://docs.unrealengine.com/5.7/en-US/meta-human-for-unreal-engine/)（无独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetaHuman/MetaHumanSDK/Tests)（仅 MetaHumanSDK 存在测试）