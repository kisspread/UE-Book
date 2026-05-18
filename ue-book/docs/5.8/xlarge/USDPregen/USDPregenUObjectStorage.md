# USDPregen

> Library to assist with pre-generating USD-based content.

| 属性 | 值 |
|---|---|
| 中文名 | USD预生成工具库 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、Python脚本、资产存储接口、HTTP处理程序） |
| 模块 | `UsdPregenCore` (Runtime), `USDPregenHttpWorker` (Runtime), `USDPregenInterchange` (Runtime), `USDPregenInterchangeEditor` (Runtime), `USDPregenPy` (Runtime), `USDPregenUObjectStorage` (Runtime), `USDPregenWrapper` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen) | |

## 用途

USDPregen 是一个专为 USD（Universal Scene Description）工作流设计的工具库，其核心目的是**在编辑器阶段或构建管线中预先处理和生成 USD 相关的资产**。这可以解决以下问题：

1.  **提升运行时性能**：通过在打包前完成耗时的 USD 解析、转换和材质编译等任务，避免运行时（尤其是启动时）的卡顿。
2.  **管线集成**：允许开发者将 USD 内容生成步骤集成到自动化的资产管线或 CI/CD 流程中。
3.  **灵活的内容管理**：提供了将 USD 元数据、依赖关系和生成规则以清单（Manifest）形式持久化存储的机制，便于跟踪和管理预生成状态。

简单来说，它不是一个运行时渲染 USD 的插件，而是一个用于“烘焙”USD 资产的“厨房助手”，确保最终用户拿到的游戏或应用中，所有 USD 相关内容都已准备就绪。

## 使用场景

- **大型开放世界游戏**：大量使用 USD 描述的植被、岩石、建筑部件。在开发阶段预生成这些资产的 UE 表示形式（Static Mesh、Material 等），打包后游戏加载更快。
- **电影级虚拟制片**：在 LED 虚拟影棚中，需要快速加载复杂的 USD 场景。USDPregen 可以提前为场景中的 USD 资产生成优化的 UE 替代资产。
- **资产协作流程**：美术使用其他 DCC 工具（如 Houdini、Maya）导出 USD，技术美术通过 USDPregen 的 Python 脚本或命令行工具，自动将这些 USD 转换并集成到 UE 项目中。
- **需要版本控制的预生成资产**：USDPregen 的清单（Manifest）系统可以记录哪些 USD 原始资产对应哪些生成的 UE 资产，当原始 USD 更新时，可以智能地重新生成受影响的部分。

## 蓝图用法

本插件 (`USDPregen`) 主要是一个底层的编辑器和运行时库，其核心功能通过 C++ 接口和 Python 脚本暴露。直接可用的蓝图节点可能较少，主要由 `USDPregenPy` 模块通过 Python 提供更高级的脚本化控制。蓝图用户通常通过编辑器菜单或命令行触发预生成流程。

### 核心节点

| 节点 | 说明 | 所在类/模块 |
|---|---|---|
| *(暂无直接暴露给蓝图的核心函数)* | 主要功能通过 Python API 和编辑器集成使用 | `USDPregenPy` |

### 使用示例（蓝图描述）

对于典型的预生成工作流，用户更多会使用 Python 脚本或编辑器工具面板。在蓝图中，可以通过 `Execute Console Command` 节点调用相关的命令行工具（如果存在），或者通过 `Py` 节点执行 Python 脚本来驱动预生成过程。具体流程取决于项目配置。

## C++ 用法

核心用法围绕 `UsdPregenCore` 模块提供的清单（Manifest）系统和 `USDPregenUObjectStorage` 提供的存储实现。以下示例展示了如何操作清单数据。

### 头文件引入

```cpp
// 使用清单和存储接口
#include "UsdPregenCore/Manifest.h"
#include "UsdPregenCore/TargetUid.h"
#include "UsdPregenUObjectStorage/USDPregenUObjectStoragePlugin.h"
#include "UsdPregenWrappers/IStorageInterface.h"
```

### 基本用法：创建和保存清单

本示例演示了创建一个简单的清单并使用 UObject 存储插件保存它。
*(来源文件路径: `USDPregenUObjectStorage/Public/USDPregenUObjectStoragePlugin.h`, `USDPregenUObjectStorage/Private/USDPregenUObjectStoragePlugin.cpp`)*

```cpp
using namespace UE::UsdPregen;

// 1. 定义一个目标唯一标识（例如，基于某个USD文件路径和配置）
FTargetUid TargetUid;
TargetUid.DefinitionUid = TEXT("MySceneDefinition");
TargetUid.PermutationUid = TEXT("DefaultPermutation");

// 2. 创建存储插件实例（通常由引擎或管理类创建）
//    参数中的选项（如内容路径）决定了清单资产存储的位置。
FPregenStorageOptions Options;
Options.ContentBasePath = TEXT("/Game/Generated/USDPregen");
FUsdPregenUObjectStoragePlugin StoragePlugin(Options);

// 3. 创建并填充一个清单对象
FManifest Manifest;
// ... 向Manifest中添加产品（Products）、依赖（Dependencies）、操作（Ops）等信息 ...
// 例如：Manifest.AddProduct(FProduct{ ... });

// 4. 序列化清单为载荷（Payload）
FManifestPayload Payload = StoragePlugin.SerializeManifest(Manifest);

// 5. 存储清单
FManifestSaveResult SaveResult = StoragePlugin.StoreManifestPayload(TargetUid, Payload);
if (SaveResult.bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Manifest stored successfully for target: %s"), *TargetUid.DefinitionUid);
}

// 6. （可选）持久化到磁盘
FManifestSaveResult PersistResult = StoragePlugin.PersistManifestPayload(TargetUid);
```

### 进阶用法：加载和更新清单

本示例展示了如何加载已存储的清单，并在其中添加新的产品信息后重新保存。
*(组合自多个头文件和使用场景推断)*

```cpp
// 承接上例，假设已有相同的 StoragePlugin 实例和 TargetUid

// 1. 加载已存在的清单载荷
FManifestLoadResult LoadResult = StoragePlugin.LoadManifestPayload(TargetUid);
if (!LoadResult.bSuccess || !LoadResult.Payload.IsSet())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to load manifest for target: %s"), *TargetUid.DefinitionUid);
    return;
}

// 2. 反序列化载荷为清单对象
FManifest ExistingManifest = StoragePlugin.DeserializeManifestPayload(LoadResult.Payload.GetValue());

// 3. 修改清单（例如，添加一个新生成的StaticMesh产品）
FProduct NewProduct;
NewProduct.UPackagePath = TEXT("/Game/Generated/USDPregen/Meshes/SM_NewAsset");
NewProduct.UClass = TEXT("StaticMesh");
NewProduct.UsdPrimPath = TEXT("/MyScene/NewAsset");
ExistingManifest.AddProduct(NewProduct);

// 4. 重新序列化并保存更新后的清单
FManifestPayload UpdatedPayload = StoragePlugin.SerializeManifest(ExistingManifest);
StoragePlugin.StoreManifestPayload(TargetUid, UpdatedPayload);
StoragePlugin.PersistManifestPayload(TargetUid); // 确保磁盘同步
```

## Demo 示例

一个演示如何定义和使用自定义存储插件的最小示例。`USDPregenUObjectStorage` 本身是 `IStorageInterface` 的一个具体实现。

```cpp
// MyCustomStoragePlugin.h
#pragma once
#include "UsdPregenWrappers/IStorageInterface.h"

class FMyCustomStoragePlugin : public UE::UsdPregen::IStorageInterface
{
public:
    virtual UE::UsdPregen::FManifestLoadResult LoadManifestPayload(const UE::UsdPregen::FTargetUid& TargetUid) override;
    virtual UE::UsdPregen::FManifestSaveResult StoreManifestPayload(
        const UE::UsdPregen::FTargetUid& TargetUid,
        const UE::UsdPregen::FManifestPayload& Payload
    ) override;
    // ... 实现其他必需接口方法 ...
private:
    // 自定义存储逻辑，例如存入数据库或自定义文件格式
};
```

```cpp
// MyCustomStoragePlugin.cpp
#include "MyCustomStoragePlugin.h"

using namespace UE::UsdPregen;

FManifestLoadResult FMyCustomStoragePlugin::LoadManifestPayload(const FTargetUid& TargetUid)
{
    FManifestPayload Payload;
    // 从你的自定义源（如SQLite数据库）根据 TargetUid 读取数据并填充 Payload
    // ...
    return FManifestLoadResult::MakeResult(Payload);
}

FManifestSaveResult FMyCustomStoragePlugin::StoreManifestPayload(
    const FTargetUid& TargetUid,
    const FManifestPayload& Payload
)
{
    // 将 Payload 数据写入你的自定义存储
    // ...
    return FManifestSaveResult::MakeResult(true);
}
// ... 其他方法的实现 ...
```

## 模块依赖

`USDPregenUObjectStorage` 模块依赖于插件的核心接口和数据结构。

| 模块 | 用途 |
|---|---|
| `UsdPregenWrapper` | 提供 `IStorageInterface` 基类、`FManifest`, `FTargetUid`, `FProduct` 等核心数据结构和前向声明。 |
| `UsdPregenCore` | 提供清单（Manifest）的实现逻辑、定义、注册等核心功能。 |

**注意**：要使用此插件的功能，你的项目模块通常需要依赖 `UsdPregenCore` 和具体的存储实现（如 `USDPregenUObjectStorage`）。依赖 `USDPregenPy` 则可以通过 Python 进行控制。

## 维护状态

### 近期更新

```
- 2026-05-14 9e86e007 [USD] UsdPregen: Fixes regression introduced by recent clean up, where an item can get incorrectly p...
- 2026-05-14 ddc18470 [USD] UsdPregen: On definition conflicts during registry population, return the existing definition ...
- 2026-05-14 60206a86 USD Pregen: Batch renaming for consistency. Also changes the default storage plugin in UE to the UOb...
- 2026-05-14 bad2257d USD Pregen: User-configurable template string with placeholders for determining asset path;
- 2026-05-14 9f286b30 USD Pregen: Fix _VT and _NonVT textures not being saved from worker imports.
```

### 维护评价

- **活跃维护**：所有提交均发生在 **2026-05-14**，表明插件正处于非常积极的开发和修复阶段。
- **实验性状态**：`.uplugin` 明确标记为 `IsBetaVersion: true` 和 `IsExperimentalVersion: true`，且默认未安装（`Installed: false`）。这意味着 API 可能不稳定，存在已知或未知的 bug。
- **核心功能明确**：从提交信息看，团队正在集中处理一致性重命名、存储默认值、路径模板配置和关键 bug 修复（如纹理保存、回归问题），说明功能框架已搭建，处于打磨期。
- **推荐程度**：**仅推荐用于实验性项目或内部工具链开发**。不建议直接用于生产环境。可以密切关注其进展，待其发布正式版本后评估使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen)
- [官方文档](https://docs.unrealengine.com) （暂无专用文档链接，请关注引擎文档更新）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen/Tests) （如果存在）