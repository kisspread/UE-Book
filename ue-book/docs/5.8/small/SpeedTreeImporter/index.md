# SpeedTree Importer

> An importer for SpeedTree runtime files.

| 属性 | 值 |
|---|---|
| 中文名 | SpeedTree 导入器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（模板材质资产） |
| 模块 | `SpeedTreeImporter` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-05-13 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/SpeedTreeImporter) | |

## 用途

SpeedTree 是业界广泛使用的树木/植被生成工具，由 IDV, Inc. 开发。此插件提供了一个编辑器内导入器，用于将 SpeedTree 运行时文件（`.srt`）导入为 Unreal Engine 可用的静态网格体（Static Mesh）资产。

该插件解决了以下核心问题：

- **格式转换**：将 SpeedTree 专有的 `.srt` 二进制格式解析为 UE 的 Static Mesh、材质和纹理资产
- **多版本兼容**：同时支持 SpeedTree v7、v8 和 v9 三种文件格式
- **LOD 管理**：支持导入 3D LOD 层级和 Billboard 贴图，并可选择将植被作为笔刷资产（Painted Foliage）或独立 Actor 使用
- **材质自动创建**：根据 SpeedTree 文件中嵌入的材质信息自动创建 UE 材质，支持法线贴图、细节贴图、高光贴图、次表面散射、风动画等选项
- **重新导入**：支持通过 Reimport 工作流更新已导入的资产，无需手动重建

此插件仅包含编辑器模块（Editor），不会被打包到最终游戏中。游戏中实际使用的 SpeedTree 渲染功能由引擎核心的 `SpeedTree` Runtime 模块提供。

## 使用场景

- 你从 SpeedTree 软件导出了 `.srt` 文件，需要将其导入 UE 项目作为场景中的树木/灌木 → 使用此导入器
- 你需要调整导入的树木比例、选择性包含碰撞体、控制材质细节（法线/高光/次表面散射等） → 在导入面板中配置 `USpeedTreeImportData` 选项
- 你在 SpeedTree 中修改了树木模型后需要更新 UE 中已有的资产 → 右键资产选择 Reimport 即可
- 你需要为大规模植被场景导入带有多级 LOD 的树木 → 选择 `3D LODs` 或 `Both` 几何体类型

## 蓝图用法

此插件为纯编辑器导入工具，不暴露任何 `BlueprintCallable` 函数。所有操作均通过编辑器界面（Content Browser 导入对话框）完成。

### 导入配置选项

导入 `.srt` 文件时会弹出配置对话框，选项来自 `USpeedTreeImportData`：

| 配置项 | 说明 | 默认分类 |
|---|---|---|
| Tree Scale | 树木整体缩放比例 | Mesh |
| Geometry | 导入几何体类型：3D LODs / Billboards / Both | Mesh |
| LOD Setup | LOD 模式：Painted Foliage / Individual Actors（仅 v8） | Mesh |
| Include Collision | 是否包含碰撞体（仅 v8） | Mesh |
| Create Materials | 是否自动创建材质（仅 v8） | Materials |
| Include Normal Maps | 包含法线贴图 | Materials |
| Include Detail Maps | 包含细节贴图 | Materials |
| Include Specular Maps | 包含高光贴图 | Materials |
| Include Branch Seam Smoothing | 包含枝干接缝平滑 | Materials |
| Include SpeedTree AO | 包含 SpeedTree 环境光遮蔽 | Materials |
| Include Random Color Variation | 包含随机颜色变化 | Materials |
| Include Subsurface | 包含次表面散射（仅 v8） | Materials |
| Include Vertex Processing | 包含顶点处理（仅 v8） | Materials |
| Include Wind | 包含风动画 | Materials |
| Include Smooth LOD | 包含平滑 LOD 过渡 | Materials |

### 使用示例

1. 在 Content Browser 中将 `.srt` 文件拖入或使用 Import 按钮
2. 弹出 SpeedTree Import Options 对话框
3. 设置 Tree Scale、Geometry 类型等参数
4. 展开 Materials 分类，勾选需要的材质特性
5. 点击 Import 完成导入
6. 后续可在 Content Browser 中右键资产 → Reimport 更新

## C++ 用法

此插件为编辑器导入框架，主要由引擎内部自动调用。以下信息供需要在代码中交互的开发者参考。

### 头文件引入

```cpp
#include "ISpeedTreeImporter.h"
#include "SpeedTreeImportData.h"
#include "SpeedTreeImportFactory.h"
```

### 检查模块可用性

```cpp
// 检查 SpeedTree 导入器模块是否已加载
if (ISpeedTreeImporter::IsAvailable())
{
    ISpeedTreeImporter& ImporterModule = ISpeedTreeImporter::Get();
    // 模块已就绪，可以使用
}
```

### 程序化导入 SpeedTree 文件

通过 Factory 可以在代码中触发导入操作：

```cpp
// 获取导入工厂
USpeedTreeImportFactory* ImportFactory = NewObject<USpeedTreeImportFactory>();

// 读取 .srt 文件
TArray<uint8> FileData;
FFileHelper::LoadFileToArray(FileData, TEXT("Path/To/Tree.srt"));

bool bOperationCanceled = false;
FFeedbackContext Warn;

// 执行导入
const uint8* Buffer = FileData.GetData();
const uint8* BufferEnd = Buffer + FileData.Num();

UObject* ImportedAsset = ImportFactory->FactoryCreateBinary(
    UStaticMesh::StaticClass(),  // 导入为 StaticMesh
    GetTransientPackage(),       // 父包
    FName("ImportedTree"),       // 资产名称
    RF_NoFlags,                  // 对象标志
    nullptr,                     // 上下文
    TEXT(".srt"),                // 文件类型
    Buffer,
    BufferEnd,
    &Warn,
    bOperationCanceled
);
```

> 注意：此方法需要在编辑器环境下运行，且依赖 `WITH_SPEEDTREE` 宏定义。实际项目中推荐直接使用 Content Browser 的导入功能。

### 自定义导入数据配置

```cpp
// 获取导入数据对象进行配置
USpeedTreeImportData* ImportData = NewObject<USpeedTreeImportData>();
ImportData->TreeScale = 1.0f;
ImportData->ImportGeometryType = IGT_3D;          // 仅导入 3D LOD
ImportData->LODType = ILT_PaintedFoliage;          // 画刷植被模式
ImportData->IncludeCollision = true;
ImportData->MakeMaterialsCheck = true;
ImportData->IncludeNormalMapCheck = true;
ImportData->IncludeWindCheck = true;
```

## Demo 示例

以下是一个最小示例，展示如何在编辑器工具中编程检查 SpeedTree 模块状态并列出支持的文件扩展名：

```cpp
// SpeedTreeUtils.h
#pragma once

#include "CoreMinimal.h"

class FSpeedTreeUtils
{
public:
    /** 检查 SpeedTree 导入器是否可用 */
    static bool IsSpeedTreeImporterAvailable();
    
    /** 获取 SpeedTree 支持的文件扩展名列表 */
    static TArray<FString> GetSupportedExtensions();
};
```

```cpp
// SpeedTreeUtils.cpp
#include "SpeedTreeUtils.h"
#include "ISpeedTreeImporter.h"

bool FSpeedTreeUtils::IsSpeedTreeImporterAvailable()
{
    return ISpeedTreeImporter::IsAvailable();
}

TArray<FString> FSpeedTreeUtils::GetSupportedExtensions()
{
    // SpeedTree 运行时文件扩展名
    return { TEXT(".srt") };
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SpeedTree` | SpeedTree 运行时核心库，提供 `.srt` 文件解析和网格体生成 |
| `MeshDescription` | 构建 StaticMesh 的中间网格描述格式 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移为 UE_LOGF 格式化方式 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 清理不再需要的 PVS 静态分析抑制标记 |
| 2025-10-20 | `6e48fe19` | [SpeedTreeImporter] | SpeedTreeImporter 相关改动 |
| 2025-09-25 | `94af5100` | Replaced PREPROCESSOR_TO_STRING with UE_STRINGIZE. | 将自定义宏替换为引擎标准 UE_STRINGIZE 宏 |
| 2025-07-14 | `8c4cad91` | Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors, and a few changes to ... | 重构 StaticMesh 的编辑器专用属性为访问器模式，涉及导入器适配 |

### 维护评价

- **创建时间**：2014 年 5 月，至今超过 11 年，属于引擎早期集成的第三方插件
- **更新频率**：近期（2025-2026）保持活跃，但更新内容以引擎基础设施适配为主（日志宏迁移、静态分析清理、API 重构适配），而非功能性改进
- **功能成熟度**：作为 SpeedTree 与 UE 的官方集成通道，功能已非常成熟稳定
- **维护模式**：被动维护——当引擎底层 API 变更时进行适配，但不会主动添加新特性
- **是否推荐使用**：✅ **推荐**。如果你使用 SpeedTree 制作植被资产，这是唯一的官方导入路径。插件本身稳定可靠，无需担心。但请注意，SpeedTree v8/v9 的部分高级功能（如 LOD Setup、次表面散射）仅在 v8+ 格式下可用

> ⚠️ 该插件已有 11 年历史，但仍在持续维护中。近期更新均为编译适配和代码规范改进，核心导入功能无变化，说明该插件已进入成熟稳定期。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/SpeedTreeImporter)
- [SpeedTree 官网](https://www.speedtree.com)