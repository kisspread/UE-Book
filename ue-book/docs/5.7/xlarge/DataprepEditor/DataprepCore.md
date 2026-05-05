# Dataprep Editor

> A tool to simplify creation and execution of data preparation pipelines from within the Unreal Editor.

| 属性 | 值 |
|---|---|
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DataprepCore` (Runtime), `DataprepEditor` (Runtime), `DataprepEditorScriptingUtilities` (Runtime), `DataprepLibraries` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-11-22 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor) | |

## 用途

Dataprep Editor 是一个企业级数据准备工具，用于在 Unreal Editor 内构建和执行数据准备管线（Pipeline）。它解决的核心问题是：**在导入大量外部资产（如 FBX、CAD 模型）后，需要进行批量的清理、优化和转换操作**。

典型的使用场景包括：
- 从 CAD/BIM 软件导入的模型通常包含大量冗余几何体、错误的材质、不合理的命名
- 需要对导入资产进行标准化处理（统一单位、清理网格、重命名、设置 LOD 等）
- 这些操作如果手动执行，耗时且容易出错

Dataprep 提供了一个可视化的管线编辑器，让用户可以：
1. **定义输入源（Producer）**：指定要处理的资产来源
2. **配置选择规则（Filter + Fetcher）**：通过属性查询精确选择要操作的对象
3. **应用操作（Operation）**：对选中对象执行转换、修改或删除
4. **定义输出（Consumer）**：将处理结果导出或保存

整个管线可以保存为资产，支持实例化和参数化，实现可重复的批处理工作流。

## 使用场景

- 你从 Revit/SketchUp 导入了建筑模型，需要批量清理冗余几何体和材质 → 用 Dataprep
- 你需要对导入的 FBX 模型进行标准化处理（重命名、设置碰撞、LOD） → 用 Dataprep
- 你需要为不同项目创建可复用的数据准备模板 → 用 Dataprep 的实例化功能
- 你需要在 CI/CD 流程中自动化资产处理 → 用 Dataprep 的命令行执行

## 蓝图用法

Dataprep 的蓝图 API 主要面向扩展开发，核心交互通过编辑器 UI 完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute` | 执行选择转换，输入对象列表，输出过滤后的对象 | `UDataprepSelectionTransform` |
| `Fetch` (Bool) | 从对象获取布尔值 | `UDataprepBoolFetcher` |
| `Fetch` (Float) | 从对象获取浮点值 | `UDataprepFloatFetcher` |
| `Fetch` (Integer) | 从对象获取整数值 | `UDataprepIntegerFetcher` |
| `Fetch` (String) | 从对象获取字符串值 | `UDataprepStringFetcher` |
| `Fetch` (StringsArray) | 从对象获取字符串数组 | `UDataprepStringsArrayFetcher` |
| `GetDisplayFetcherName` | 获取 Fetcher 的显示名称 | `UDataprepFetcher` |
| `GetDisplayTransformName` | 获取 Transform 的显示名称 | `UDataprepSelectionTransform` |
| `GetCategory` | 获取 Transform 的分类 | `UDataprepSelectionTransform` |

### 使用示例（蓝图描述）

**创建自定义 Fetcher（蓝图）：**
1. 创建新的蓝图类，父类选择 `DataprepStringFetcher`
2. 重写 `Fetch` 函数：接收 `Object` 参数，返回从该对象提取的字符串
3. 设置 `bOutFetchSucceeded` 为 true 表示成功获取
4. 在 Dataprep 编辑器中即可使用该 Fetcher

**创建自定义 SelectionTransform（蓝图）：**
1. 创建新的蓝图类，父类选择 `DataprepSelectionTransform`
2. 重写 `OnExecution` 函数：接收 `InObjects`，处理后输出到 `OutObjects`
3. 设置 `bOutputCanIncludeInput` 控制是否保留原始对象

## C++ 用法

### 头文件引入

```cpp
#include "DataprepCoreUtils.h"
#include "DataprepAsset.h"
#include "DataprepOperation.h"
#include "SelectionSystem/DataprepFilter.h"
#include "SelectionSystem/DataprepFetcher.h"
#include "SelectionSystem/DataprepSelectionTransform.h"
```

### 基本用法

**执行 Dataprep 资产（来自 DataprepCoreUtils）：**

```cpp
// 来源: Engine/Plugins/Enterprise/DataprepEditor/Source/DataprepCore/Public/DataprepCoreUtils.h

// 获取 Dataprep 资产并执行
UDataprepAsset* DataprepAsset = LoadObject<UDataprepAsset>(nullptr, TEXT("/Game/MyDataprepPipeline"));

// 创建日志和进度报告器
TSharedPtr<IDataprepLogger> Logger = MakeShared<FMyDataprepLogger>();
TSharedPtr<IDataprepProgressReporter> Reporter = MakeShared<FMyProgressReporter>();

// 执行完整的管线（导入、处理、导出）
bool bSuccess = FDataprepCoreUtils::ExecuteDataprep(DataprepAsset, Logger, Reporter);
```

**创建自定义 Fetcher（C++）：**

```cpp
// 来源: Engine/Plugins/Enterprise/DataprepEditor/Source/DataprepCore/Public/SelectionSystem/DataprepStringFetcher.h

UCLASS()
class UMyCustomStringFetcher : public UDataprepStringFetcher
{
    GENERATED_BODY()

public:
    // 重写 Fetch 函数，从对象提取字符串数据
    virtual FString Fetch_Implementation(const UObject* Object, bool& bOutFetchSucceeded) const override
    {
        if (const AActor* Actor = Cast<AActor>(Object))
        {
            bOutFetchSucceeded = true;
            return Actor->GetActorLabel();
        }
        bOutFetchSucceeded = false;
        return FString();
    }

    // 可选：自定义 UI 显示名称
    virtual FText GetDisplayFetcherName_Implementation() const override
    {
        return NSLOCTEXT("MyPlugin", "ActorNameFetcher", "Actor Name");
    }
};
```

### 进阶用法

**创建自定义 Operation：**

```cpp
// 来源: Engine/Plugins/Enterprise/DataprepEditor/Source/DataprepCore/Public/DataprepOperation.h

UCLASS()
class UMyDataprepOperation : public UDataprepOperation
{
    GENERATED_BODY()

public:
    // 操作的执行逻辑
    virtual void OnExecution_Implementation(const FDataprepContext& InContext) override
    {
        for (UObject* Object : InContext.Objects)
        {
            if (AStaticMeshActor* MeshActor = Cast<AStaticMeshActor>(Object))
            {
                // 对静态网格执行操作
                // 使用 GetAddAssetDelegate() 创建资产副本
                // 使用 GetRemoveObjectDelegate() 移除对象
            }
        }
    }

    // 操作的分类
    virtual FText GetCategory_Implementation() const override
    {
        return FDataprepOperationCategories::MeshOperation;
    }
};
```

**使用参数化系统：**

```cpp
// 来源: Engine/Plugins/Enterprise/DataprepEditor/Source/DataprepCore/Public/Parameterization/DataprepParameterizationUtils.h

// 从属性句柄创建参数化链
TSharedPtr<IPropertyHandle> PropertyHandle = /* 从 Details Panel 获取 */;
TArray<FDataprepPropertyLink> PropertyChain = FDataprepParameterizationUtils::MakePropertyChain(PropertyHandle);

// 验证属性链是否有效
if (FDataprepParameterizationUtils::IsPropertyChainValid(PropertyChain))
{
    // 可以进行参数化绑定
}

// 获取对象所属的 Dataprep 资产
UDataprepAsset* Asset = FDataprepParameterizationUtils::GetDataprepAssetForParameterization(MyObject);
```

**使用进度报告器：**

```cpp
// 来源: Engine/Plugins/Enterprise/DataprepEditor/Source/DataprepCore/Public/IDataprepProgressReporter.h

void MyLongRunningOperation(const TSharedPtr<IDataprepProgressReporter>& Reporter)
{
    // 创建工作报告器，自动管理 BeginWork/EndWork
    FDataprepWorkReporter WorkReporter(Reporter, 
        NSLOCTEXT("MyPlugin", "Processing", "Processing Assets..."), 
        100.0f,  // 总工作量
        10.0f);  // 每步增量

    for (int32 i = 0; i < 10; ++i)
    {
        // 检查是否被取消
        if (WorkReporter.IsWorkCancelled())
        {
            break;
        }

        // 处理一批资产...
        WorkReporter.ReportNextStep(
            FText::Format(NSLOCTEXT("MyPlugin", "Progress", "Processing batch {0}"), FText::AsNumber(i)));
    }
    // WorkReporter 析构时自动调用 EndWork
}
```

## Demo 示例

**自定义 Float Fetcher - 获取 Actor 的缩放值：**

```cpp
// MyScaleFetcher.h
#pragma once

#include "SelectionSystem/DataprepFloatFetcher.h"
#include "MyScaleFetcher.generated.h"

UCLASS(meta = (DisplayName = "Actor Scale"))
class UMyScaleFetcher : public UDataprepFloatFetcher
{
    GENERATED_BODY()

public:
    virtual float Fetch_Implementation(const UObject* Object, bool& bOutFetchSucceeded) const override;
    virtual FText GetDisplayFetcherName_Implementation() const override;
    virtual FText GetTooltipText_Implementation() const override;
};
```

```cpp
// MyScaleFetcher.cpp
#include "MyScaleFetcher.h"
#include "GameFramework/Actor.h"

float UMyScaleFetcher::Fetch_Implementation(const UObject* Object, bool& bOutFetchSucceeded) const
{
    if (const AActor* Actor = Cast<AActor>(Object))
    {
        bOutFetchSucceeded = true;
        return Actor->GetActorScale3D().X; // 返回 X 轴缩放
    }
    
    bOutFetchSucceeded = false;
    return 0.0f;
}

FText UMyScaleFetcher::GetDisplayFetcherName_Implementation() const
{
    return NSLOCTEXT("MyPlugin", "ScaleFetcher", "Actor Scale (X)");
}

FText UMyScaleFetcher::GetTooltipText_Implementation() const
{
    return NSLOCTEXT("MyPlugin", "ScaleTooltip", "Fetches the X-axis scale of an Actor");
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | 数据交换核心框架 |
| `InterchangeEngine` | 数据交换引擎 |
| `InterchangeNodes` | 交换节点定义 |
| `InterchangeImport` | 导入功能 |
| `InterchangeExport` | 导出功能 |
| `MeshDescription` | 网格描述数据结构 |
| `StaticMeshDescription` | 静态网格描述 |
| `MeshConversion` | 网格转换工具 |
| `AssetRegistry` | 资产注册表 |
| `Json` | JSON 序列化 |
| `DesktopPlatform` | 桌面平台功能 |
| `ToolMenus` | 工具菜单系统 |
| `GraphEditor` | 图表编辑器 |
| `KismetCompiler` | 蓝图编译器 |
| `BlueprintGraph` | 蓝图图表 |

## 维护状态

### 近期更新

```
- 63ce8c7164f6 [Truncation Warnings] Update EdGraphNode and EdGraph API to use FVector2f
- b059f7b46335 Fix trivial unreachable code warnings.
- 4fa54a66b901 Fixed Dataprep editor crashes - Root cause: Order of serialization then deserialization were wrong. Dependent obects were create first. Fixed. - Root cause: Interchange import returns the editor's map as a imported object. THis will be investigated in another JIRA. Fixed by triaging assets generated by Interchange. - Root cause: Initial implementation was caching viewport's actors used to which mesh components were attached. Fixed by removing those actors and recreating them each time the preview viewport is updated.
```

### 维护评价

Dataprep Editor 是一个**成熟的企业级插件**，由 Epic Games 官方维护。

**优点：**
- 功能完整，覆盖了数据准备的完整工作流
- 架构设计良好，支持扩展（自定义 Fetcher、Filter、Operation、Producer、Consumer）
- 支持参数化和实例化，适合团队协作
- 有完善的日志和进度报告系统

**注意事项：**
- 默认未启用（`EnabledByDefault: false`），需要在插件设置中手动启用
- 主要面向企业用户（Enterprise 分类），适合处理大规模资产导入场景
- 与 Interchange 框架深度集成，是 UE5 数据导入管线的核心组件
- 近期更新主要是编译警告修复和崩溃修复，功能层面已趋于稳定

**推荐使用：** 如果你的项目涉及大量外部资产导入（CAD、BIM、FBX 等），且需要标准化的批处理流程，Dataprep 是官方推荐的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/dataprep-editor-in-unreal-engine/)