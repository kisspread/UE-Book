# Bridge

> Megascans Link for Quixel Bridge.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 桥接 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有 |
| 模块 | `Bridge` (Editor), `MegascansPlugin` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-09 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Bridge) | |

## 用途

Bridge 插件是连接 Quixel Bridge 桌面应用程序与 Unreal Engine 5 的核心桥梁。它解决了艺术家和开发者在 Unreal Editor 中高效发现、管理、预览和导入 Quixel Megascans 3D 资产库的问题。通过此插件，用户无需离开编辑器即可访问数以千计的高质量 PBR 资产，并将其无缝集成到项目中，极大地提升了写实场景的构建效率。

## 使用场景

- 你正在开发一个需要高度真实感的开放世界游戏 → 使用 Bridge 插件快速填充环境，如岩石、植被、地面材质。
- 你需要为建筑可视化项目寻找逼真的室内外资产 → 通过 Bridge 插件直接从 Quixel Bridge 下载并导入。
- 你需要为 MetaHuman 角色搭配写实的服装和配饰 → 通过 Bridge 插件导入相关的 3D 资产。

## 蓝图用法

插件的核心功能主要通过编辑器 UI 和操作暴露，部分底层管理功能提供蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsBridgeConnected` | 检查与 Quixel Bridge 应用程序的连接状态 | `UBridgeConnectionManager` |
| `ImportAssetFromJson` | 从 JSON 数据导入资产（内部调用） | `UMegascansImportManager` |
| `GetContentBrowserPath` | 获取资产在内容浏览器中的预期路径 | `UMegascansImportManager` |

### 使用示例（蓝图描述）

在蓝图中，你可以创建一个简单的连接状态检查器：
1. 使用 `Get Bridge Connection Manager` 节点获取连接管理器单例。
2. 连接 `Is Bridge Connected` 节点到其执行引脚。
3. 将布尔返回值连接到一个 Branch 节点。
4. True 分支可以触发一个提示或更新 UI，指示插件就绪。
通常，资产的浏览和直接导入通过编辑器窗口完成，蓝图主要用于扩展自动化流程。

## C++ 用法

### 头文件引入

```cpp
#include "BridgeConnectionManager.h"
#include "MegascansImportManager.h"
```

### 基本用法

检查与 Quixel Bridge 的连接状态。
```cpp
// 检查连接状态
UBridgeConnectionManager* ConnectionManager = UBridgeConnectionManager::Get();
if (ConnectionManager && ConnectionManager->IsBridgeConnected())
{
    UE_LOG(LogTemp, Log, TEXT("Quixel Bridge 已连接，可以导入资产。"));
}
```

### 进阶用法

监听资产导入完成事件，以便进行后续处理。
```cpp
// 订阅资产导入完成委托
UMegascansImportManager* ImportManager = UMegascansImportManager::Get();
ImportManager->OnAssetImported.AddLambda([](const FAssetData& ImportedAsset)
{
    UE_LOG(LogTemp, Log, TEXT("新资产已导入: %s"), *ImportedAsset.AssetName.ToString());
    // 在此处对新导入的资产执行操作，例如设置材质参数、生成实例等
});
```

## Demo 示例

**BridgeModuleDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "BridgeModuleDemo.generated.h"

class UBridgeConnectionManager;
class UMegascansImportManager;

UCLASS()
class UBridgeModuleDemo : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    void OnAssetImported(const FAssetData& ImportedAsset);
};
```

**BridgeModuleDemo.cpp**
```cpp
#include "BridgeModuleDemo.h"
#include "BridgeConnectionManager.h"
#include "MegascansImportManager.h"

void UBridgeModuleDemo::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 1. 检查 Bridge 连接
    UBridgeConnectionManager* ConnMgr = UBridgeConnectionManager::Get();
    if (ConnMgr)
    {
        bool bConnected = ConnMgr->IsBridgeConnected();
        UE_LOG(LogTemp, Log, TEXT("Bridge 初始化：连接状态 = %s"), bConnected ? TEXT("已连接") : TEXT("未连接"));
    }

    // 2. 订阅资产导入事件
    UMegascansImportManager* ImportMgr = UMegascansImportManager::Get();
    if (ImportMgr)
    {
        ImportMgr->OnAssetImported.AddUObject(this, &UBridgeModuleDemo::OnAssetImported);
    }
}

void UBridgeModuleDemo::Deinitialize()
{
    // 取消订阅
    UMegascansImportManager* ImportMgr = UMegascansImportManager::Get();
    if (ImportMgr)
    {
        ImportMgr->OnAssetImported.RemoveAll(this);
    }
    Super::Deinitialize();
}

void UBridgeModuleDemo::OnAssetImported(const FAssetData& ImportedAsset)
{
    UE_LOG(LogTemp, Warning, TEXT("Demo 模块捕获到资产导入: %s"), *ImportedAsset.GetSoftObjectPath().ToString());
}
```

## 模块依赖

从 Build.cs 提取，插件需要以下独特模块支持：

| 模块 | 用途 |
|---|---|
| `Megascans` | 核心 Megascans 资产类型和处理逻辑 |
| `WebBrowser` | 内嵌浏览器用于与 Bridge 应用程序通信 |
| `ContentBrowser` | 与内容浏览器集成，显示导入进度和资产 |
| `AssetTools` | 资产导入、管理等底层操作 |
| `EditorScriptingUtilities` | 提供编辑器脚本工具功能 |
| `MetaHumanSDK` | 与 MetaHuman 工作流集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4797537` | Fix crash in UMaterialPresetsSettings::PostEditChangeProperty when master material slots are empty o | 修复了主材质插槽为空时材质预设设置导致的崩溃。 |
| 2026-04-16 | `aea11131` | Clean up WebBrowser module and init settings, handle module init failures | 清理 WebBrowser 模块代码和初始化设置，并处理模块初始化失败的情况。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 日志宏迁移为更安全的 UE_LOGF 格式。 |
| 2026-04-06 | `3e98cc7e` | TLazyObjectPtr Deprecation pt 3: | 继续推进移除已废弃的 TLazyObjectPtr 类型的工作。 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 涉及资产保存流程的调整或修复。 |

### 维护评价

Bridge 插件处于**活跃维护**状态。虽然它已存在约 5 年，但近几个月（2026年）仍有持续的功能性修复和底层代码改进（如崩溃修复、依赖清理、日志规范更新）。作为 Quixel Megascans 资产进入 Unreal 的官方主要通道，其实用性和维护优先级很高。推荐在需要高质量 Megascans 资产的写实项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Bridge)
- [官方文档](https://help.quixel.com/hc/en-us/sections/360005846137-Quixel-Bridge-for-Unreal-Engine-5)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Bridge/Tests)