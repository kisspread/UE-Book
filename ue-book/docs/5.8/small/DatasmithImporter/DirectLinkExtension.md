# Datasmith Importer

> Importer for Datasmith files.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数据桥接导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

DatasmithImporter 是 UE5 中用于从外部 DCC（数字内容创作）工具导入场景数据的企业级导入框架。它的核心价值在于提供了一套**无需中间文件格式**的实时数据同步机制——通过 DirectLink 协议，3ds Max、Revit、SketchUp、SolidWorks 等应用程序可以直接将场景变更推送到 Unreal Engine，省去了传统的导出/导入流程。

本插件不是单一的文件导入器，而是一个**模块化的数据桥接平台**：
- **DirectLinkExtension**：DirectLink 通信层，管理端点连接、源发现、自动重连
- **DatasmithTranslator / NativeTranslator**：将外部格式翻译为 UE 可识别的 `IDatasmithScene`
- **DatasmithImporter**：将翻译后的场景转化为 UE 资产（StaticMesh、Material、Actor 等）
- **ExternalSource**：抽象外部数据源，支持 URI 定位和懒加载

整个架构的设计理念是**解耦通信与翻译**——DirectLink 只负责数据传输，具体的格式解析由各 Translator 模块完成。

## 使用场景

- 你正在做建筑可视化项目，使用 Revit / SketchUp 建模 → 通过 DirectLink 实时同步到 UE，无需反复导出 FBX
- 你有一个大型工业 CAD 场景（SolidWorks / CATIA）→ 用 Datasmith 的原生翻译器导入 NURBS 和层级结构
- 你需要一个资产在源应用修改后自动更新 → 开启 DirectLink 的 Auto-Reimport 功能
- 你在做一个管线工具，需要程序化获取可用的 DirectLink 源 → 通过 URI 系统解析和定位源

## 蓝图用法

DirectLinkExtension 模块暴露了两个蓝图可调用函数，均位于 `Editor Scripting | DirectLink` 分类下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAvailableDirectLinkSourcesUri` | 获取当前所有可用 DirectLink 源的 URI 列表 | `UDirectLinkExtensionBlueprintLibrary` |
| `ParseDirectLinkSourceUri` | 将 DirectLink URI 字符串解析为计算机名、端点名、可执行文件名、源名 | `UDirectLinkExtensionBlueprintLibrary` |

### 使用示例（蓝图描述）

**获取并连接 DirectLink 源：**

1. 添加 `Get Available Direct Link Sources Uri` 节点，输出为 `TArray<FString>`
2. 用 `ForEachLoop` 遍历每个 URI 字符串
3. 对每个 URI 调用 `Parse Direct Link Source Uri`，可获取：
   - `Out Computer Name`：运行 DCC 应用的计算机名称
   - `Out Endpoint Name`：DirectLink 端点名称
   - `Out Executable Name`：DCC 应用程序名称（如 "3dsmax"、"revit"）
   - `Out Source Name`：场景/数据源名称
4. 根据解析结果过滤你关心的源（例如只处理来自特定计算机的源）

**URI 格式示例：**

```
directlink://ComputerName/EndpointName/ExecutableName/SourceName?SourceId=GUID
```

## C++ 用法

### 头文件引入

```cpp
#include "DirectLinkExtensionModule.h"
#include "IDirectLinkManager.h"
#include "DirectLinkExternalSource.h"
#include "DirectLinkUriResolver.h"
#include "DirectLinkExtensionSettings.h"
```

### 基本用法：获取 DirectLink 管理器并列出可用源

```cpp
// 来源: Public/DirectLinkExtensionModule.h, Public/IDirectLinkManager.h

#include "DirectLinkExtensionModule.h"

// 检查 DirectLink 模块是否可用
if (IDirectLinkExtensionModule::IsAvailable())
{
    // 获取管理器单例
    IDirectLinkManager& Manager = IDirectLinkExtensionModule::Get().GetManager();

    // 获取所有已发现的 DirectLink 外部源
    TArray<TSharedRef<FDirectLinkExternalSource>> Sources = Manager.GetExternalSourceList();

    for (const TSharedRef<FDirectLinkExternalSource>& Source : Sources)
    {
        UE_LOG(LogTemp, Log, TEXT("源名称: %s, 可用: %s, 同步状态: %s"),
            *Source->GetSourceName(),
            Source->IsAvailable() ? TEXT("是") : TEXT("否"),
            Source->IsOutOfSync() ? TEXT("过期") : TEXT("同步"));
    }
}
```

### 基本用法：通过 URI 获取外部源

```cpp
// 来源: Public/IDirectLinkManager.h, Public/DirectLinkUriResolver.h

#include "DirectLinkExtensionModule.h"

// 构造 DirectLink URI
FSourceUri Uri;
Uri.SetScheme(TEXT("directlink"));
// ... 设置 URI 各组件

// 通过 URI 获取外部源（自动创建或返回缓存）
IDirectLinkManager& Manager = IDirectLinkExtensionModule::Get().GetManager();
TSharedPtr<FDirectLinkExternalSource> ExternalSource = Manager.GetOrCreateExternalSource(Uri);

if (ExternalSource.IsValid())
{
    // 打开 DirectLink 流连接
    bool bSuccess = ExternalSource->OpenStream();
    UE_LOG(LogTemp, Log, TEXT("流连接: %s"), bSuccess ? TEXT("成功") : TEXT("失败"));
}
```

### 基本用法：启用资产自动重新导入

```cpp
// 来源: Public/IDirectLinkManager.h

#include "DirectLinkExtensionModule.h"

IDirectLinkManager& Manager = IDirectLinkExtensionModule::Get().GetManager();

UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/ImportedMesh"));

// 为资产启用自动重新导入
// 当 DirectLink 源更新时，资产会自动重新导入
if (Manager.SetAssetAutoReimport(Mesh, true))
{
    UE_LOG(LogTemp, Log, TEXT("已为 %s 启用自动重新导入"), *Mesh->GetName());
}

// 检查资产的自动重新导入状态
bool bEnabled = Manager.IsAssetAutoReimportEnabled(Mesh);
```

### 进阶用法：自定义 ExternalSource 类型注册

```cpp
// 来源: Public/IDirectLinkManager.h

#include "DirectLinkExtensionModule.h"
#include "DirectLinkExternalSource.h"

// 假设你有一个自定义的 DirectLink 外部源类型
class FMyCustomExternalSource : public FDirectLinkExternalSource
{
public:
    explicit FMyCustomExternalSource(const FSourceUri& InSourceUri)
        : FDirectLinkExternalSource(InSourceUri)
    {}

    virtual bool CanOpenNewConnection(
        const DirectLink::IConnectionRequestHandler::FSourceInformation& Source) override
    {
        // 自定义连接判断逻辑
        return true;
    }

protected:
    virtual TSharedPtr<DirectLink::ISceneReceiver> GetSceneReceiverInternal(
        const DirectLink::IConnectionRequestHandler::FSourceInformation& Source) override
    {
        // 返回自定义的场景接收器
        return nullptr;
    }
};

// 注册自定义类型
IDirectLinkManager& Manager = IDirectLinkExtensionModule::Get().GetManager();
Manager.RegisterDirectLinkExternalSource<FMyCustomExternalSource>(FName("MyCustomSource"));
```

### 进阶用法：自定义 URI 解析器

```cpp
// 来源: Public/DirectLinkExtensionModule.h

#include "DirectLinkExtensionModule.h"
#include "DirectLinkUriResolver.h"

// 注册自定义的 URI 解析器，覆盖默认行为
TSharedRef<UE::DatasmithImporter::IUriResolver> MyResolver = 
    MakeShared<FMyCustomUriResolver>();

IDirectLinkExtensionModule::Get().OverwriteUriResolver(MyResolver);
```

### 进阶用法：使用 DirectLink 端点

```cpp
// 来源: Public/DirectLinkExtensionModule.h, Private/DirectLinkManager.h

#include "DirectLinkExtensionModule.h"

// 获取底层 DirectLink 端点，用于低级别操作
DirectLink::FEndpoint& Endpoint = IDirectLinkExtensionModule::GetEndpoint();

// 端点是 DirectLink 协议的核心：
// - 维护与所有外部源的连接
// - 接收状态变化通知（通过 IEndpointObserver）
// - 管理源发现和连接协商
```

### 进阶用法：解析 DirectLink URI 组件

```cpp
// 来源: Public/DirectLinkUriResolver.h

#include "DirectLinkUriResolver.h"

FSourceUri Uri;
// 假设 Uri 已经被正确设置

TOptional<FDirectLinkSourceDescription> Description = 
    FDirectLinkUriResolver::TryParseDirectLinkUri(Uri);

if (Description.IsSet())
{
    UE_LOG(LogTemp, Log, TEXT("计算机: %s"), *Description->ComputerName);
    UE_LOG(LogTemp, Log, TEXT("可执行文件: %s"), *Description->ExecutableName);
    UE_LOG(LogTemp, Log, TEXT("端点名: %s"), *Description->EndpointName);
    UE_LOG(LogTemp, Log, TEXT("源名称: %s"), *Description->SourceName);

    if (Description->SourceId.IsSet())
    {
        UE_LOG(LogTemp, Log, TEXT("源ID: %s"), *Description->SourceId->ToString());
    }
}
```

## Demo 示例

### 最小可运行示例：扫描并连接 DirectLink 源

```cpp
// MyDirectLinkDemo.h
#pragma once

#include "CoreMinimal.h"

class FMyDirectLinkDemo
{
public:
    /** 扫描所有可用的 DirectLink 源并打印信息 */
    static void ScanAvailableSources();

    /** 连接到第一个可用的 DirectLink 源 */
    static bool ConnectToFirstAvailableSource(UObject* AssetToAutoReimport = nullptr);

    /** 断开所有连接 */
    static void DisconnectAll();
};
```

```cpp
// MyDirectLinkDemo.cpp
#include "MyDirectLinkDemo.h"
#include "DirectLinkExtensionModule.h"
#include "IDirectLinkManager.h"
#include "DirectLinkExternalSource.h"

void FMyDirectLinkDemo::ScanAvailableSources()
{
    if (!IDirectLinkExtensionModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("DirectLinkExtension 模块未加载"));
        return;
    }

    IDirectLinkManager& Manager = IDirectLinkExtensionModule::Get().GetManager();
    TArray<TSharedRef<FDirectLinkExternalSource>> Sources = Manager.GetExternalSourceList();

    UE_LOG(LogTemp, Log, TEXT("=== 发现 %d 个 DirectLink 源 ==="), Sources.Num());

    for (int32 i = 0; i < Sources.Num(); ++i)
    {
        const FDirectLinkExternalSource& Source = Sources[i].Get();
        UE_LOG(LogTemp, Log, TEXT("[%d] 名称: %s | 可用: %s | 过期: %s | 哈希: %s"),
            i,
            *Source.GetSourceName(),
            Source.IsAvailable() ? TEXT("✓") : TEXT("✗"),
            Source.IsOutOfSync() ? TEXT("是") : TEXT("否"),
            *LexToString(Source.GetSourceHash()));
    }
}

bool FMyDirectLinkDemo::ConnectToFirstAvailableSource(UObject* AssetToAutoReimport)
{
    if (!IDirectLinkExtensionModule::IsAvailable())
    {
        return false;
    }

    IDirectLinkManager& Manager = IDirectLinkExtensionModule::Get().GetManager();
    TArray<TSharedRef<FDirectLinkExternalSource>> Sources = Manager.GetExternalSourceList();

    // 找到第一个可用源
    for (const TSharedRef<FDirectLinkExternalSource>& Source : Sources)
    {
        if (Source->IsAvailable() && !Source->IsStreamOpen())
        {
            if (Source->OpenStream())
            {
                UE_LOG(LogTemp, Log, TEXT("已连接到: %s"), *Source->GetSourceName());

                // 可选：为指定资产启用自动重新导入
                if (AssetToAutoReimport && Manager.SetAssetAutoReimport(AssetToAutoReimport, true))
                {
                    UE_LOG(LogTemp, Log, TEXT("已启用自动重新导入: %s"), *AssetToAutoReimport->GetName());
                }

                return true;
            }
        }
    }

    UE_LOG(LogTemp, Warning, TEXT("没有可用的 DirectLink 源"));
    return false;
}

void FMyDirectLinkDemo::DisconnectAll()
{
    if (!IDirectLinkExtensionModule::IsAvailable())
    {
        return;
    }

    IDirectLinkManager& Manager = IDirectLinkExtensionModule::Get().GetManager();
    TArray<TSharedRef<FDirectLinkExternalSource>> Sources = Manager.GetExternalSourceList();

    for (const TSharedRef<FDirectLinkExternalSource>& Source : Sources)
    {
        if (Source->IsStreamOpen())
        {
            Source->CloseStream();
            UE_LOG(LogTemp, Log, TEXT("已断开: %s"), *Source->GetSourceName());
        }
    }
}
```

## 模块依赖

Build.cs 未直接提供，以下依赖从头文件中的类型引用推断：

| 模块 | 用途 |
|---|---|
| `DirectLink` | Epic 的实时数据交换协议核心库，提供 FEndpoint、FSourceHandle、ISceneReceiver 等基础类型 |
| `ExternalSource` | 外部数据源抽象层，提供 FExternalSource 基类、FSourceUri、IUriResolver 接口 |
| `DatasmithCore` | Datasmith 核心类型定义，提供 IDatasmithScene 等场景表示接口 |

> 注：该插件默认未启用（`EnabledByDefault: false`），需在 Edit → Plugins 中手动启用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的截断警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 废弃旧版对象遍历 API，引入新的替代方案 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理纹理属性修改代码，规范使用编辑变更回调 |
| 2026-03-05 | `1adb9f68` | New material translator work | 新材质翻译器开发工作 |

### 维护评价

DatasmithImporter 是 **Epic Games 官方维护的企业级插件**，自 2019 年创建以来持续活跃更新。从近期 git 记录看，它仍在进行**实质性功能开发**（新材质翻译器）和**代码质量维护**（API 迁移、警告修复），最近一次更新距今不到 1 个月。

**优势**：
- Epic 官方维护，长期支持有保障
- 活跃更新，与 UE 引擎版本同步迭代
- 8 个模块的模块化架构，扩展性强
- 支持数十种 DCC 格式的实时数据同步

**注意事项**：
- 插件默认未启用，需手动开启
- DirectLink 功能需要外部应用（如 3ds Max）也安装了 Datasmith 插件才能建立连接
- 作为企业版功能，文档和社区资源相对较少
- 模块间依赖关系复杂，二次开发需要理解完整的 Translator → ExternalSource → Manager 管线

**推荐**：如果你的项目涉及 CAD/BIM/AEC 工作流，这是一个**必备插件**。即使是纯游戏项目，在需要从专业建模软件导入复杂场景时也值得启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [DirectLinkExtension 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkExtension)
- [测试用例（DirectLinkTest 模块）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest)