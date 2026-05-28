# Dataprep Editor

> A tool to simplify creation and execution of data preparation pipelines from within the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 数据准备编辑器 |
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产定义、样式资源） |
| 模块 | `DataprepCore` (Runtime), `DataprepEditor` (Runtime), `DataprepEditorScriptingUtilities` (Runtime), `DataprepLibraries` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-11-22 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor) | |

## 用途

Dataprep Editor 是一个可视化数据准备管线工具，允许用户在 Unreal Editor 内构建可复用的数据处理管线。它解决的核心问题是：**在将外部资产（CAD、BIM、点云等）导入 UE 时，需要进行大量重复的数据清洗、转换和优化操作**。

传统的做法是编写脚本或手动逐个处理资产，而 Dataprep Editor 提供了：
- **可视化管线编辑器**：类似蓝图的节点图，用拖拽方式构建数据处理流程
- **过滤器系统**：按名称、类型、数值、字符串等条件筛选对象
- **操作（Operations）**：对筛选出的对象执行变换、合并、材质处理等操作
- **预览系统**：在执行前预览每一步的结果，包括场景预览和资产预览
- **生产者/消费者架构**：从多种来源导入数据，输出到不同目标
- **参数化系统**：将管线中的属性绑定到参数，支持实例化复用
- **统计面板**：执行前后对比三角形、顶点、材质、纹理等统计数据

该插件面向企业用户，特别是汽车、建筑、制造行业的数字孪生场景，需要批量处理大量导入资产的用例。

## 使用场景

- 你在导入大量 CAD/BIM 模型后需要自动移除不需要的部件（如螺丝、内部结构）→ 用 Dataprep 过滤器 + 删除操作
- 你需要批量合并静态网格体以减少 Draw Calls → 用 Dataprep 合并操作
- 你想为所有导入的资产统一设置 LOD 或碰撞 → 用 Dataprep 操作管线
- 你需要在每次导入时自动应用相同的材质替换规则 → 创建可复用的 Dataprep Asset 管线
- 你想让非程序员也能配置数据导入流程 → 用 Dataprep 的可视化编辑器

## 蓝图用法

> 注意：Dataprep Editor 主要通过编辑器 UI 操作，蓝图集成有限。核心工作流在编辑器内完成。

### 模块接口

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateDataprepProducersWidget` | 创建生产者配置 UI 控件 | `IDataprepEditorModule` |
| `CreateDataprepDetailsView` | 创建详情视图控件 | `IDataprepEditorModule` |

### 编辑器面板概述

Dataprep Editor 打开后包含以下面板：

| 面板 | 功能 |
|---|---|
| Scene Preview（场景预览） | 显示场景大纲，与预览系统联动 |
| Asset Preview（资产预览） | 树形结构展示所有资产，支持筛选和排序 |
| Graph Editor（图编辑器） | 可视化管线编辑，拖拽构建操作流程 |
| Palette（调色板） | 可用的过滤器和操作列表 |
| Details（详情） | 选中节点的属性编辑 |
| Statistics（统计） | 执行前后的资产统计数据对比 |
| Scene Viewport（场景视口） | 3D 视口，支持线框、X-Ray 等多种渲染模式 |

### 核心工作流（编辑器操作）

1. **创建 Dataprep Asset**：右键 Content Browser → Dataprep → Dataprep Asset
2. **添加生产者（Producer）**：在 Producers 面板中选择数据源类型
3. **构建管线**：在图编辑器中从 Palette 拖拽 Filter 和 Operation 到 Action 节点
4. **预览结果**：点击步骤预览，查看过滤器的效果
5. **执行管线**：工具栏按钮执行完整管线
6. **提交世界**：将结果提交到目标世界/资产

## C++ 用法

### 头文件引入

```cpp
#include "DataprepEditorModule.h"
```

### 基本用法：获取编辑器模块接口

```cpp
// 获取 Dataprep 编辑器模块单例
IDataprepEditorModule& DataprepEditorModule = IDataprepEditorModule::Get();

// 检查模块是否可用
if (IDataprepEditorModule::IsAvailable())
{
    // 创建生产者配置控件
    TSharedRef<SWidget> ProducersWidget = DataprepEditorModule.CreateDataprepProducersWidget(AssetProducers);
}
```

### 进阶用法：创建详情视图

```cpp
// 创建自定义的 Dataprep 详情视图
TSharedRef<SWidget> DetailsView = DataprepEditorModule.CreateDataprepDetailsView(MyObject);

// 注册菜单和工具栏扩展
// IDataprepEditorModule 继承自 IHasMenuExtensibility 和 IHasToolBarExtensibility
// 可通过 GetMenuExtensibilityManager() 和 GetToolBarExtensibilityManager() 添加自定义扩展
```

### 进阶用法：访问编辑器实例

```cpp
// FDataprepEditor 是主要的编辑器类，继承自 FAssetEditorToolkit
// 通过资产定义（UAssetDefinition_DataprepAsset）打开编辑器时自动创建

// 获取关联的 Dataprep 资产
UDataprepAssetInterface* DataprepAsset = DataprepEditor->GetDataprepAsset();

// 获取预览世界
UWorld* PreviewWorld = DataprepEditor->GetWorld();

// 获取世界选择集
const TSet<TWeakObjectPtr<UObject>>& SelectedItems = DataprepEditor->GetWorldItemsSelection();

// 设置预览系统观察的步骤
TArray<UDataprepParameterizableObject*> Steps;
DataprepEditor->SetPreviewedObjects(Steps);

// 同步选择到预览系统
DataprepEditor->SyncSelectionToPreviewSystem();

// 监听资产生产者/消费者变化
DataprepEditor->OnDataprepAssetProducerChanged().AddLambda([]()
{
    // 处理生产者变化
});
```

## Demo 示例

以下示例展示如何从代码中访问 Dataprep 编辑器系统并查询预览状态：

```cpp
// MyDataprepHelper.h
#pragma once

#include "CoreMinimal.h"

class UDataprepAssetInterface;
class FDataprepEditor;

class FMyDataprepHelper
{
public:
    /** 检查当前是否有 Dataprep 编辑器打开 */
    static bool IsDataprepEditorOpen();
    
    /** 获取当前预览系统中通过过滤器的对象数量统计 */
    static void GetPreviewStats(UDataprepAssetInterface* Asset, int32& OutPassCount, int32& OutFailCount);
};
```

```cpp
// MyDataprepHelper.cpp
#include "MyDataprepHelper.h"
#include "DataprepEditorModule.h"
#include "DataprepCore/Public/DataprepAssetInterface.h"

bool FMyDataprepHelper::IsDataprepEditorOpen()
{
    return IDataprepEditorModule::IsAvailable();
}

void FMyDataprepHelper::GetPreviewStats(UDataprepAssetInterface* Asset, int32& OutPassCount, int32& OutFailCount)
{
    OutPassCount = 0;
    OutFailCount = 0;
    
    if (!Asset || !IDataprepEditorModule::IsAvailable())
    {
        return;
    }
    
    // 通过模块接口创建详情视图来访问资产
    IDataprepEditorModule& Module = IDataprepEditorModule::Get();
    TSharedRef<SWidget> DetailsView = Module.CreateDataprepDetailsView(Asset);
    
    // 注意：完整的预览系统访问需要在编辑器上下文中
    // FDataprepPreviewSystem 提供了 GetPreviewDataForObject() 方法
    // 来查询每个对象的预览状态（Pass/Fail/BeingProcessed/NotSupported）
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DataprepCore` | 核心数据类型和资产定义（UDataprepAsset、过滤器、操作基类等） |
| `DataprepLibraries` | 内置的过滤器和操作库实现 |
| `SceneOutliner` | 场景大纲面板集成 |
| `AssetDefinition` | 资产类型定义和打开行为 |
| `AdvancedPreviewScene` | 3D 预览场景支持 |
| `PropertyEditor` | 属性编辑器和详情面板自定义 |
| `GraphEditor` | 图编辑器框架（节点图 UI） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复浮点精度截断警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. | 废弃旧的对象遍历 API |
| 2026-03-23 | `42dfe52f` | Consolidate PreviewFeatureLevelChanged and PreviewPlatformChanged into a single PreviewShaderPlatformChanged delegate. | 合并预览平台变更委托 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now... | 清理过时的头文件包含 |

### 维护评价

- **创建于 2019 年**，属于 Epic Games 官方维护的企业级插件
- **持续维护中**：最近的提交在 2026 年 5 月，且保持了规律的更新频率（约每月 1-2 次）
- 近期更新主要是**代码现代化**：修复编译警告、迁移日志宏、清理废弃 API、重构代理接口
- 没有功能性大改动，说明该插件**功能已趋于稳定**
- `EnabledByDefault = false`，需要在插件管理器中手动启用
- **建议使用**：对于需要批量数据准备的企业项目，该插件是官方推荐方案，维护状态良好

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor)
- [官方文档](https://docs.unrealengine.com/)（.uplugin 中 DocsURL 为空，参考 UE 官方文档搜索 "Dataprep"）