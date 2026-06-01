# Warp Utils

> PFM/MPCDI generation & visualization

| 属性 | 值 |
|---|---|
| 中文名 | 投影融合工具 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产） |
| 模块 | `PFMExporter` (Runtime), `WarpUtils` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-18 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WarpUtils) | |

## 用途

该插件为 **nDisplay** 系统提供核心的投影几何校正与色彩融合支持。它主要用于生成和处理 **PFM** 文件（一种存储每像素相机映射信息的格式）以及 **MPCDI** 文件（一种标准化的投影仪配置数据格式）。这些文件是驱动多投影仪系统进行精确的**几何扭曲 (Warp)** 和**边缘融合 (Blend)** 的基础数据，确保多个投影仪投射出的图像在物理空间上能够无缝拼接，形成一个完整的、无畸变的沉浸式视觉画面。

## 使用场景

- **大型沉浸式投影环境**：如飞行模拟器、赛车模拟器、穹顶影院等，需要多个投影仪协同工作以覆盖整个视野。
- **主题公园与黑暗骑乘**：在复杂曲面上进行精确投影。
- **企业级沉浸式展厅**：利用多投影仪创建大型环幕或CAVE系统。
- **任何需要将UE场景渲染到非平面或经过几何校正的投影表面上的项目**。

## 蓝图用法

该插件的核心功能偏向于底层数据处理和管线集成，其提供的蓝图节点主要用于启动和控制导出流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportPFM` | 启动PFM文件生成流程，用于导出特定相机视角下的像素映射数据。 | `UPFMExporterSubsystem` |

### 使用示例（蓝图描述）

在需要为 nDisplay 配置生成校正数据的蓝图中，可以调用 `ExportPFM` 节点。通常需要指定目标相机、输出分辨率以及要保存的文件路径。该节点会触发后台计算，生成对应的PFM文件，供后续的投影融合软件或 nDisplay 配置工具使用。

## C++ 用法

### 头文件引入

```cpp
#include "PFMExporter.h"
```

### 基本用法

通过 `PFMExporterSubsystem` 子系统来请求导出 PFM 文件。

```cpp
// 假设在某个 GameInstance 或管理器类中
#include "Subsystems/SubsystemCollection.h"
#include "PFMExporter.h"

void ExportCameraPFM()
{
    if (UWorld* World = GetWorld())
    {
        // 从世界获取子系统
        if (UPFMExporterSubsystem* PFMExporter = World->GetSubsystem<UPFMExporterSubsystem>())
        {
            // 构建导出参数
            FPFMExportSettings ExportSettings;
            ExportSettings.CameraActor = MyCameraActor; // 指定要生成映射数据的相机
            ExportSettings.Resolution = FIntPoint(1920, 1080); // 目标分辨率
            ExportSettings.OutputPath = FPaths::ProjectSavedDir() / TEXT("PFMOutput.pfm");
            
            // 请求导出（可能是异步的）
            PFMExporter->RequestExport(ExportSettings);
        }
    }
}
```

## Demo 示例

由于该插件为 nDisplay 基础设施的一部分，通常不会独立使用。其典型使用方式是通过 nDisplay 的编辑器工具或配置流程触发。一个最小化的 C++ 示例就是上面的 `ExportCameraPFM` 函数，展示了如何从 C++ 代码触发 PFM 导出。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorFramework` | PFMExporter模块依赖，用于编辑器集成 |
| `UnrealEd` | PFMExporter模块依赖，用于访问编辑器功能进行数据导出 |

**注意**：`WarpUtils` 模块的依赖在提供的文档中未明确列出，根据其Runtime性质推断，可能仅依赖引擎核心模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，代码现代化 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理做准备，添加必要包含 |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 适配RHI命令列表接口变更，重构纹理创建 |
| 2025-01-21 | `42de2ffc` | Merging RHI CreateBuffer refactor to Main. | 适配RHI缓冲区创建重构 |
| 2024-02-22 | `01203093` | Deprecate: | 对某些API进行废弃标记 |

### 维护评价

WarpUtils 是一个为 nDisplay 系统服务的**基础设施类插件**，创建于约 7 年前，目前仍处于 **Beta** 状态且**默认禁用**。

- **维护模式**：插件仍在持续维护中，以适应 UE 引擎底层 API 的迭代（如 RHI 接口的变更、日志系统升级）。
- **功能状态**：其核心功能（PFM/MPCDI 生成）在 nDisplay 生态中已成熟应用，但插件本身作为独立单元可能仍被标记为实验性。
- **推荐度**：**仅推荐给 nDisplay 或自定义多投影仪显示系统的开发者使用**。普通项目无需关注。使用时请注意其 `IsBetaVersion=true` 的状态以及 `PlatformAllowList: Win64` 的平台限制（至少PFMExporter模块仅支持Win64）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WarpUtils)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WarpUtils/Tests) （如果存在）