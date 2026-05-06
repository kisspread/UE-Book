# Flow Production Tracking

> Flow Production Tracking (formerly known as Shotgun and/or ShotGrid) integration for the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 流程制作跟踪（Flow） |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Shotgrid` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Shotgrid) | |

## 用途

该插件将 **Flow Production Tracking**（原 Shotgun / ShotGrid）集成到 Unreal Editor 中，通过 **Python 脚本** 在编辑器和 Shotgrid 平台之间建立桥梁。它提供了一套 C++ 基础框架（`UShotgridEngine`）和 UI 管理逻辑，允许用户从 Unreal Editor 内直接调用 Shotgrid 命令、管理上下文（当前选中的资产或 Actor）以及同步元数据。

**为什么存在？**  
传统上，美术/动画管线依赖 Shotgrid 进行任务管理和资源追踪。该插件解决了在 Unreal Editor 中无需离开编辑器即可与 Shotgrid 交互的问题：  
- 通过蓝图/Python 桥接，可扩展自定义命令。  
- 自动传递选中资产/Actor 作为上下文，方便 Shotgrid 端记录操作。  
- 支持将自定义元数据标签写入资产注册表，便于在 Shotgrid 中查询。

## 使用场景

- **影视 / 游戏制作管线**：团队使用 Flow Production Tracking 管理资产版本、任务状态，希望在 Unreal Editor 中直接检查/更新资产信息。  
- **自定义工具集成**：开发者在 Shotgrid 中定义一组命令（如“发布资产”、“导出材质”），通过该插件在 UE 编辑器中触发执行。  
- **元数据同步**：需要将 UE 资产的某些标记（如 `ShotgunAssetId`）注册到资产注册表，供其他工具或 Shotgrid 调用使用。

## 蓝图用法

插件的核心交互类为 `UShotgridEngine`，它公开了可供蓝图表单调用的静态函数以及可重写的事件（`BlueprintImplementableEvent`）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInstance` | 获取当前 Python Shotgrid 引擎的单例实例 | `UShotgridEngine` |
| `GetShotgridWorkDir` | 获取 Shotgrid 工作区根目录路径 | `UShotgridEngine` |
| `GetReferencedAssets` | 获取给定 Actor 引用的所有资产对象 | `UShotgridEngine` |
| `OnEngineInitialized` | 当 Python 引擎初始化完成时调用的回调 | `UShotgridEngine` |
| `GetShotgridMenuItems`（事件） | 由 Python 端实现，返回可用的菜单命令列表 | `UShotgridEngine` |
| `ExecuteCommand`（事件） | 由 Python 端实现，执行指定名称的 Shotgrid 命令 | `UShotgridEngine` |
| `Shutdown`（事件） | 由 Python 端实现，关闭 Shotgrid 引擎 | `UShotgridEngine` |

### 使用示例（蓝图描述）

1. **获取引擎实例并执行命令**  
   - 在关卡蓝图或自定义蓝图函数中调用 `Get Shotgrid Engine`（`UShotgridEngine::GetInstance`）得到 `ShotgridEngine` 对象。  
   - 将其连接到 `Execute Command` 节点，并输入命令名称（如 `"PublishAsset"`）。该节点是蓝图事件，实际由 Python 后端执行。  
   - 在此之前可调用 `Set Selection`（C++ 函数，在编辑器逻辑中自动调用）传递当前选中的资产和 Actor。

2. **获取工作目录**  
   - 直接调用 `Get Shotgrid Work Dir` 静态函数，返回字符串路径，可用于创建或读取文件。

3. **获取引用资产**  
   - 通过 `Get Referenced Assets` 输入一个 Actor，返回该 Actor 的所有引用资产（`UObject*` 数组），常用于上下文传递。

## C++ 用法

### 头文件引入

```cpp
#include "IShotgridModule.h"
#include "ShotgridEngine.h"
#include "ShotgridSettings.h"
```

### 基本用法

从 `IShotgridModule` 获取模块实例，与 `UShotgridEngine` 交互。

**例：获取引擎实例并执行命令**（源自 `ShotgridEngine.h` 的使用模式）

```cpp
// 确保模块加载
IShotgridModule& Module = IShotgridModule::Get();

// 获取 Shotgrid 引擎实例
UShotgridEngine* Engine = UShotgridEngine::GetInstance();
if (Engine)
{
    // 触发 Python 端实现的命令
    Engine->ExecuteCommand(TEXT("PublishLevel"));
}
```

**例：设置当前选中的资产和 Actor**（由 UI 管理代码内部调用）

```cpp
void MyTool::OnSelectionChanged(const TArray<FAssetData>& SelectedAssets, const TArray<AActor*>& SelectedActors)
{
    UShotgridEngine* Engine = UShotgridEngine::GetInstance();
    if (Engine)
    {
        Engine->SetSelection(&SelectedAssets, &SelectedActors);
    }
}
```

### 进阶用法

**自定义元数据标签注册**：

在 `UShotgridSettings` 中可配置需要汇入资产注册表的元数据标签。通过修改 `MetaDataTagsForAssetRegistry` 属性，插件会自动将这些标签写入资产注册表，方便外部工具查询。

```cpp
// 在项目设置中配置后，通过 PostInitProperties / PostEditChangeProperty 自动生效
const UShotgridSettings* Settings = GetDefault<UShotgridSettings>();
for (const FName& Tag : Settings->MetaDataTagsForAssetRegistry)
{
    // 这些标签将在资产注册时被保留
}
```

**创建自定义 Python 引擎实现**（继承 `UShotgridEngine`）：

1. 在 Blueprint 中新建一个蓝图类，父类设为 `ShotgridEngine`。  
2. 实现 `Get Shotgrid Menu Items`、`Execute Command`、`Shutdown` 事件。  
3. 将蓝图实例设置为 Python 引擎的后端（需配合 PythonScriptPlugin 加载）。

## Demo 示例

以下是一个最小的 C++ 编辑器工具示例，展示如何接收选中资产并打印引用资产路径。

**MyShotgridTool.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "IShotgridModule.h"
#include "ShotgridEngine.h"

class FMyShotgridTool
{
public:
    static void PrintReferencedAssets(const AActor* Actor);
};
```

**MyShotgridTool.cpp**
```cpp
#include "MyShotgridTool.h"
#include "AssetRegistry/AssetData.h"

void FMyShotgridTool::PrintReferencedAssets(const AActor* Actor)
{
    UShotgridEngine* Engine = UShotgridEngine::GetInstance();
    if (!Engine || !Actor) return;

    TArray<UObject*> ReferencedAssets = Engine->GetReferencedAssets(Actor);
    for (UObject* Obj : ReferencedAssets)
    {
        if (Obj)
        {
            UE_LOG(LogTemp, Log, TEXT("Referenced Asset: %s"), *Obj->GetPathName());
        }
    }
}
```

**在编辑器模块中使用**（例如 `FShotgridUIManagerImpl` 内部可调用此工具）。

## 模块依赖

由于插件是 Editor 类型，并且依赖 Python 脚本和编辑器脚本工具，其 Build.cs 中引入了独特依赖：

| 模块 | 用途 |
|---|---|
| `PythonScriptPlugin` | 提供 Python 解释器，用于执行 Shotgrid Python 引擎 |
| `EditorScriptingUtilities` | 提供编辑器脚本相关的函数（如资产操作、Actor 操作） |

其余依赖为标准编辑器插件常见模块（Core, Engine, UnrealEd 等），此处省略。

## 维护状态

### 近期更新

- 2024-08-27 `32811c8a` — Rename shotgrid to Flow Production Tracking. Fix startup issue with Flow trying to run before python plugin initialization.
- 2023-01-16 `bbc37aa2` — General engine updates.
- 2022-10-21 `610c4676` — Update vendor links for built-in plugins to use secure protocol.
- 2022-09-18 `de37b387` — FName → FSoftObjectPath refactoring.
- 2022-08-18 `3f4252aa` — ObjectPtr upgrade for engine plugins.

### 维护评价

- **创建时间**：2022-08-18，约 2 年，属于较新的插件。  
- **最近更新**：2024-08-27 存在功能修复和重命名，表明仍在维护。  
- **活跃度**：约 1 次/年的大更新，属于低频率但持续维护。  
- **注意事项**：插件标记为 **实验性**（`IsBetaVersion=true`），API 可能变动，且需要在项目中手动启用。  
- **推荐使用**：如果你的团队已经使用 Flow Production Tracking 且需要深度 UE 集成，可以尝试使用；但建议先在非生产环境中验证稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Shotgrid)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/flow-production-tracking-in-unreal-engine/)（未从 .uplugin 获取，但依据 UE 官方文档结构推断）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Shotgrid/Tests)（未公开，但可通过 Git 历史探索）