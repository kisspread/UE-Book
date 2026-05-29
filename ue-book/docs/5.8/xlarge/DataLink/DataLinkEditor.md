# Motion Design Data Link

> 

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计数据链接 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

DataLink 是一个基于节点图的数据链接系统，专为虚拟制片中的动态设计（Motion Design）场景打造。它解决了**将不同数据源（HTTP、WebSocket、DataTable、JSON）与运动设计资产进行实时数据对接**的问题。

核心设计理念：
- **图编辑器驱动**：使用 Unreal 的图编辑器（Graph Editor）可视化编排数据流转
- **编译管线**：将可视化图编译为运行时可执行的数据链（FDataLinkNode 链）
- **多源数据接入**：支持 HTTP 请求、WebSocket 实时连接、DataTable 查询、JSON 解析等多种数据源
- **编辑器预览**：无需运行游戏即可在编辑器中测试数据链的输入输出

该插件最初位于 `Engine/Plugins/Experimental/` 下，后迁移至 `Engine/Plugins/VirtualProduction/`，目前处于 Beta 状态。

## 使用场景

- 你在做虚拟制片的动态图形（Motion Graphics），需要从外部 API 实时拉取数据 → 用 DataLink 的 HTTP 模块
- 你需要通过 WebSocket 接收实时数据流并驱动场景中资产的属性变化 → 用 DataLink 的 WebSocket 模块
- 你想通过可视化节点图编排复杂的数据转换管线 → 用 DataLinkGraph 编辑器
- 你需要在编辑器中快速预览数据链的输入输出，调试数据流转逻辑 → 用 DataLink 预览工具

## 蓝图用法

当前模块（DataLinkEditor）主要提供编辑器扩展功能，蓝图 API 较少。核心的蓝图暴露 API 在运行时模块中。

### 核心数据类型

| 类型 | 说明 | 所在头文件 |
|---|---|---|
| `FDataLinkInstance` | 数据链接实例，包含图引用和输入数据 | `DataLink` (Runtime) |
| `FDataLinkInputData` | 输入数据描述，含显示名和数据值 | `DataLink` (Runtime) |
| `FInstancedStruct` | 输出数据（可变结构体） | `DataLink` (Runtime) |
| `EDataLinkExecutionResult` | 执行结果枚举 | `DataLink` (Runtime) |

### 编辑器接口

| 接口 | 说明 | 所在类 |
|---|---|---|
| `FindPreviewOutputData()` | 获取当前预览输出数据 | `IDataLinkEditorMenuContext` |
| `GetAssetPath()` | 获取当前编辑资产的路径 | `IDataLinkEditorMenuContext` |

### 预览数据对象

在编辑器中预览数据链时，`UDataLinkPreviewData` 提供了输入和输出的编辑界面：

| 属性 | 访问方式 | 说明 |
|---|---|---|
| `DataLinkInstance` | EditAnywhere | 可编辑的数据链接实例（含图 + 输入） |
| `OutputData` | VisibleAnywhere | 只读的输出数据 |

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkEditorModule.h"
#include "DataLinkGraphAssetEditor.h"
#include "DataLinkGraphCompiler.h"
#include "DataLinkPreviewTool.h"
```

### 基本用法：编译数据链图

从 `FDataLinkGraphCompiler` 的使用模式提取：

```cpp
// 创建编译器并编译数据链图
UDataLinkGraph* DataLinkGraph = /* 获取或创建数据链图 */;
FDataLinkGraphCompiler Compiler(DataLinkGraph);

// 执行编译
UE::DataLink::EGraphCompileStatus Status = Compiler.Compile();

// 检查编译结果
if (Status == UE::DataLink::EGraphCompileStatus::Success)
{
    // 编译成功，DataLinkGraph 的运行时数据已更新
    UE_LOG(LogDataLinkEditor, Log, TEXT("Data link graph compiled successfully"));
}
```
*来源：Private/Compiler/DataLinkGraphCompiler.h*

### 基本用法：创建资产编辑器

```cpp
// 初始化数据链图资产编辑器
UDataLinkGraph* DataLinkGraph = /* 加载或创建 */;
UDataLinkGraphAssetEditor* AssetEditor = NewObject<UDataLinkGraphAssetEditor>();
AssetEditor->Initialize(DataLinkGraph);

// 获取图编辑器工具包
TSharedPtr<FDataLinkGraphAssetToolkit> Toolkit = AssetEditor->GetToolkit();
```
*来源：Private/DataLinkGraphAssetEditor.h*

### 进阶用法：预览数据链执行

```cpp
// 创建预览工具（通常由 AssetToolkit 自动管理）
UDataLinkGraphAssetEditor* AssetEditor = /* 获取编辑器 */;
FDataLinkPreviewTool PreviewTool(AssetEditor);

// 初始化预览工具
PreviewTool.Initialize();

// 预览工具内部会：
// 1. 从 PreviewData 获取输入数据（FDataLinkInstance）
// 2. 创建 FDataLinkExecutor 执行数据链
// 3. 通过 FDataLinkSink 接收输出
// 4. 在 OnPreviewOutputData 回调中处理结果
```
*来源：Private/Preview/DataLinkPreviewTool.h*

### 进阶用法：属性自定义

```cpp
// FDataLinkInstanceCustomization 为 FDataLinkInstance 提供自定义属性面板
// 当图编译完成后，会自动更新输入数据的显示
void FDataLinkInstanceCustomization::OnGraphCompiled(UDataLinkGraph* InDataLinkGraph)
{
    // 图编译后，刷新输入数据以匹配新的输入 pin
    UpdateInputData();
}

// FDataLinkInputDataCustomization 为每个输入项提供自定义显示
// 显示名称从 DisplayNameHandle 属性获取
FText FDataLinkInputDataCustomization::GetInputDisplayName() const
{
    // 返回输入数据的用户友好名称
    return FText::FromName(/* 从属性句柄获取 */);
}
```
*来源：Private/DetailsView/DataLinkInstanceCustomization.h, DataLinkInputDataCustomization.h*

## Demo 示例

一个最小的编辑器扩展示例，展示如何访问预览输出数据：

```cpp
// MyDataLinkMenuContext.h
#pragma once

#include "IDataLinkEditorMenuContext.h"
#include "MyDataLinkMenuContext.generated.h"

UCLASS()
class UMyDataLinkMenuContext : public UObject, public IDataLinkEditorMenuContext
{
    GENERATED_BODY()

public:
    virtual FConstStructView FindPreviewOutputData() const override
    {
        // 返回最新的预览输出数据
        // 注意：用户随时可能使视图失效，因此视图应视为短生命周期
        return FConstStructView();
    }

    virtual FString GetAssetPath() const override
    {
        return TEXT("/Game/MyDataLinkAsset");
    }
};
```

```cpp
// MyDataLinkEditorActions.cpp
#include "DataLinkGraphCompiler.h"
#include "DataLinkEditorLog.h"

DEFINE_LOG_CATEGORY(LogMyDataLink);

void CompileMyGraph(UDataLinkGraph* InGraph)
{
    if (!InGraph)
    {
        UE_LOG(LogMyDataLink, Error, TEXT("Invalid data link graph"));
        return;
    }

    FDataLinkGraphCompiler Compiler(InGraph);
    UE::DataLink::EGraphCompileStatus Status = Compiler.Compile();

    switch (Status)
    {
    case UE::DataLink::EGraphCompileStatus::Success:
        UE_LOG(LogMyDataLink, Log, TEXT("Graph compiled successfully"));
        break;
    default:
        UE_LOG(LogMyDataLink, Warning, TEXT("Graph compilation failed"));
        break;
    }
}
```

## 模块依赖

从 Build.cs 文件分析，DataLinkEditor 模块依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心运行时模块，提供数据链接的执行引擎 |
| `DataLinkEdGraph` | 图编辑器节点定义，提供编辑时的图表示 |
| `GraphEditor` | Unreal 图编辑器框架 |
| `DataLinkGraphCompiler` | 图编译器（内嵌于 DataLinkEditor） |

无特殊依赖（仅标准 Core/Engine/Slate 等框架模块及上述 DataLink 专用模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 支持 FString 和 FSharedString 两种字符串类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 新日志宏 |
| 2026-03-02 | `e97b93d4` | Fixes for CL 51336460 - Remove string duplication in FJsonObject to free memory | 修复 FJsonObject 中的字符串重复以释放内存 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 字符串重复以优化内存 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退变更 CL51209244 |

### 维护评价

**活跃维护中** ✅

- **创建时间**：2025-08-27，约 1 年前从 Experimental 迁移至 VirtualProduction
- **最近更新频率**：最近 3 个月内有多次实质性更新（内存优化、代码重构、日志迁移）
- **维护状态**：活跃维护中，持续有功能性改进
- **已知限制**：标记为 Beta 版本（`IsBetaVersion: true`），API 可能发生变化
- **推荐使用**：适合虚拟制片项目使用，但需注意 Beta 状态，生产环境使用需谨慎评估

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink)
- 官方文档：暂无
- 测试用例：暂未发现公开的自动化测试文件