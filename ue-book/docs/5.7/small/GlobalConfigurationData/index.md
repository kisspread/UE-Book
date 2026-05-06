# Global Configuration Data

> A system that is used to query configuration data that can come from many different sources without knowing specifically which one.

| 属性 | 值 |
|---|---|
| 中文名 | 全局配置数据 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GlobalConfigurationData` (Runtime), `GlobalConfigurationDataCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData) | |

---

## 总体用途

该插件提供了一组核心工具和运行时模块，用于**统一查询来自多种来源的配置数据**。它抽象了数据源的细节（如本地文件、远程服务器、热修复补丁等），上层代码只需通过标准接口获取配置，而无需关心数据具体来自哪里。适用于需要灵活、可扩展配置管理的项目，例如 A/B 测试、远程热修复、环境特定设置等。

---

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `GlobalConfigurationDataCore` | Runtime | 核心数据结构和基础接口，定义查询 API 与数据源抽象。 |
| `GlobalConfigurationData` | Runtime | 运行时注册与管理模块，提供默认路由器、控制台命令等高层功能。 |
| `GlobalConfigurationDataTests` | Runtime | 自动化测试模块，覆盖核心与运行时的单元测试及 BDD 用例。 |

各模块的详细 API 文档请参阅：
- [GlobalConfigurationData 模块](GlobalConfigurationData.md)
- [GlobalConfigurationDataCore 模块](GlobalConfigurationDataCore.md)
- [GlobalConfigurationDataTests 模块](GlobalConfigurationDataTests.md)

---

## 使用场景

- **多环境配置管理**：开发、测试、生产环境使用不同的配置源，代码无需改动。
- **动态热修复**：通过远程服务器下发配置，无需重新打包即可调整参数。
- **A/B 测试**：根据用户组或设备 ID 查询差异化配置。
- **降低耦合**：业务逻辑只依赖配置键，不依赖具体数据源实现。

---

## 蓝图用法

该插件当前为实验性，主要提供 C++ 接口。如果模块导出了蓝图可调用函数，会在各模块文档中列出。请参阅对应模块文档。

---

## C++ 用法

### 头文件引入

```cpp
#include "GlobalConfigurationDataCore.h"
#include "GlobalConfigurationDataModule.h"
```

### 基本用法

通过 `IGlobalConfigurationDataSubsystem` 或核心 API 查询配置：

```cpp
// 获取配置子系统（需在 GameInstance 初始化后）
if (auto* Subsystem = GEngine->GetEngineSubsystem<UGlobalConfigurationDataSubsystem>())
{
    // 查询整型配置，默认值 42
    int32 Value = Subsystem->GetInt(TEXT("MySetting"), 42);
}
```

详细示例和进阶用法（如自定义数据源、JSON 扁平化自动处理等）请参考各模块文档及测试用例。

---

## Demo 示例

建议直接运行测试模块 `GlobalConfigurationDataTests` 中的自动化测试。测试用例覆盖了核心查询、多源合并、热修复路由等场景，是学习使用的最佳入口。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Json` | 处理 JSON 配置数据的解析与序列化 |
| `JsonUtilities` | 提供 JSON 对象的工具函数 |
| `DeveloperSettings` | 允许在项目设置中配置默认数据源 |

其他常见依赖（Core、CoreUObject、Engine 等）已省略。

---

## 维护状态

### 近期更新

- 2025-09-10 `61b63b3f` [GCD] Add support to auto flatten json objects with a single entry
- 2025-07-18 `10de61f9` [GCD] Make console command router debug only, add a 'hotfix' config router for high priority setting
- 2025-06-23 `bfa3140f` [Misc] Fix GlobalConfigurationData test ensures
- 2025-06-17 `8a2ca4d6` [UE] Add experimental Global Configuration Data

### 维护评价

该插件于 2025 年 6 月作为实验性功能添加，至今已有多次功能性更新（JSON 扁平化、热修复路由器）和 Bug 修复。最新提交在 2025 年 9 月，表明仍在活跃开发中。虽然是实验性插件，API 可能不稳定，但功能明确、更新积极，适合需要灵活配置管理的新项目先行试用。建议关注未来版本中 API 的稳定性变化。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData/Tests)
- 官方文档：暂无（实验性插件）