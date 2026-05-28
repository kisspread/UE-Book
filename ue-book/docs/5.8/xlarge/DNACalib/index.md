# DNACalib Plugin

> DNA Calibration tool plugin

| 属性 | 值 |
|---|---|
| 中文名 | DNA 校准工具 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DNACalibLib` (Runtime), `DNACalibLibTest` (Runtime), `DNACalibModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DNACalib) | |

## 用途

DNACalib 是面向 MetaHuman 面部动画管线的 **DNA 数据校准工具**。在 UE 的动画体系中，"DNA" 是一种描述面部骨骼驱动器（Facial Rig）配置的数据格式，由 RigLogic 运行时读取并驱动面部动画。

DNACalib 的核心职责是对 DNA 数据进行**后处理与变换**，包括但不限于：

- **坐标系转换**：将 DNA 文件中的面法线朝向（face winding）从源坐标系转换到 UE 所需的坐标系，支持任意坐标系输入
- **畸形数据修复**：检测并处理格式不规范的 DNA 文件，提高加载鲁棒性
- **性能优化**：通过减少数据拷贝提升 DNA 资产加载性能，同时保持向后兼容
- **序列化修复**：解决多平台环境下 DNAConfig 访问的数据竞争问题

简而言之：**RigLogic 负责"读"DNA，DNACalib 负责"修"DNA**。

## 使用场景

- 你从 DCC 工具（Maya/Blender）导出 MetaHuman 面部 DNA，需要转换坐标系适配 UE → 用 DNACalib 的 face-winding 转换
- 你收到的 DNA 文件格式不规范，加载时报错 → 用 DNACalib 的畸形数据容错处理
- 你需要在运行时优化 DNA 资产的加载速度 → DNACalib 已内置零拷贝优化
- 你正在构建 MetaHuman 面部动画管线的批量预处理流水线 → 用 DNACalibLib C++ API 进行脚本化处理

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| [DNACalibLib](DNACalibLib.md) | Runtime (C++) | 核心校准算法库，提供 DNA 数据变换、坐标系转换、数据修复等底层能力 |
| [DNACalibLibTest](DNACalibLibTest.md) | Runtime | DNACalibLib 的自动化测试模块（仅 Win64） |
| [DNACalibModule](DNACalibModule.md) | Runtime | UE 模块入口层，负责模块注册与引擎集成 |

### 模块依赖关系

```
DNACalibModule ──► UnrealEd
DNACalibLib    ──► UnrealEd
DNACalibLibTest ──► DNACalibLib
```

三个模块均依赖 **RigLogic** 插件（在 .uplugin 中声明为插件级依赖）。

## 快速开始

该插件默认未启用。要使用 DNACalib，需要在项目中手动启用插件，并确保 **RigLogic** 插件已启用：

1. 在项目 `.uproject` 中添加：
```json
{
    "Plugins": [
        { "Name": "DNACalib", "Enabled": true },
        { "Name": "RigLogic", "Enabled": true }
    ]
}
```

2. 在模块 `Build.cs` 中添加依赖：
```csharp
PublicDependencyModuleNames.Add("DNACalibLib");
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2f6aa301` | Improve DNA asset load performance and backwards compatible conversion by reducing data copies | 优化 DNA 资产加载性能，减少数据拷贝并保持向后兼容 |
| 2026-05-12 | `57c5e2c7` | Update DNA and RigLogic to better handle malformed DNA files | 增强对畸形 DNA 文件的容错处理能力 |
| 2026-05-12 | `0577289d` | Suppress private module include warnings for test modules (RigLogicLibTest, DNACalibLibTest, DNACali | 消除测试模块的私有头文件引用编译警告 |
| 2026-04-30 | `82833e51` | Fix data-race on per platform DNAConfig access during serialization | 修复多平台序列化时 DNAConfig 的数据竞争问题 |
| 2026-04-28 | `0c7a803e` | Implement face-winding conversion in DNA to support arbitrary coordinate systems in UE | 实现 DNA 面法线朝向转换，支持任意坐标系 |

### 维护评价

**活跃维护**。DNACalib 创建于 2024 年 10 月，至今约 1.6 年，近期（2026 年 4-5 月）仍有多次实质性功能更新，涵盖性能优化、bug 修复、坐标系支持等核心改进。该插件随 RigLogic 插件协同维护，是 MetaHuman 面部动画管线的关键组成部分，建议放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DNACalib)
- [DNACalibLib 模块文档](DNACalibLib.md)
- [DNACalibLibTest 模块文档](DNACalibLibTest.md)
- [DNACalibModule 模块文档](DNACalibModule.md)
- 依赖插件：[RigLogic](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic)