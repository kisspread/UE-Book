# AudioSynesthesiaEditor 模块

> 编辑器模块，提供分析器资产的工厂类和资产类型操作，使分析器设置和 NRT 结果可在内容浏览器中创建和管理。

| 属性 | 值 |
|---|---|
| 类型 | Editor |
| 加载阶段 | PostDefault |
| 头文件 | 8 个 (.h) |
| 源文件 | 8 个 (.cpp) |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | 编辑器工具 |
| `AudioSynesthesia` | 分析器类定义 |
| `AudioAnalyzer` | 分析器基类 |
| `InputCore` | 输入核心 |
| `Slate` / `SlateCore` | UI 框架 |
| `EditorStyle` | 编辑器样式 |
| `AssetTools`（私有头文件引用） | 资产工具 |

## 功能概述

本模块负责在 Unreal 编辑器中注册分析器资产类型，使用户可以：

1. **在内容浏览器中创建分析器设置资产**（右键 → Audio → Synesthesia）
2. **在内容浏览器中创建 NRT 分析结果资产**
3. **资产显示自定义颜色和子菜单**

## 资产工厂类

### UAudioSynesthesiaSettingsFactory

**头文件**: `Classes/AudioSynesthesiaSettingsFactory.h`

创建实时分析器设置资产的工厂。在内容浏览器中右键 → Audio → Synesthesia Settings 下显示所有可用的设置类型。

### UAudioSynesthesiaNRTSettingsFactory

**头文件**: `Classes/AudioSynesthesiaNRTSettingsFactory.h`

创建 NRT 分析器设置资产的工厂。

### UAudioSynesthesiaNRTFactory

**头文件**: `Classes/AudioSynesthesiaNRTFactory.h`

创建 NRT 分析结果资产的工厂。用户先创建 NRT 资产，指定 SoundWave 和设置，然后触发分析。

## 资产类型操作

### AssetTypeActions_AudioSynesthesiaSettings

**头文件**: `Private/AssetTypeActions_AudioSynesthesiaSettings.h`

为实时分析器设置资产注册编辑器操作：
- 自定义缩略图颜色
- 子菜单分类

### AssetTypeActions_AudioSynesthesiaNRTSettings

**头文件**: `Private/AssetTypeActions_AudioSynesthesiaNRTSettings.h`

为 NRT 设置资产注册编辑器操作。

### AssetTypeActions_AudioSynesthesiaNRT

**头文件**: `Private/AssetTypeActions_AudioSynesthesiaNRT.h`

为 NRT 结果资产注册编辑器操作。

## 辅助类

### AudioSynesthesiaClassFilter

**头文件**: `Private/AudioSynesthesiaClassFilter.h`

资产选择器的类过滤器，用于在 UI 中筛选可用的分析器类型。

## 编辑器中的工作流

1. **创建设置资产**: 内容浏览器右键 → Audio → Synesthesia Settings → 选择分析器类型（Loudness、ConstantQ、Meter、LKFS、Spectrum）
2. **配置参数**: 在细节面板中调整分析参数
3. **创建 NRT 资产**（离线分析）: 右键 → Audio → Synesthesia NRT → 选择类型 → 指定 SoundWave 和设置 → 触发分析
4. **使用结果**: 在蓝图中引用 NRT 资产，调用查询函数获取特定时间点的分析数据

## 源码链接

- [AudioSynesthesiaEditor 模块目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioSynesthesia/Source/AudioSynesthesiaEditor)
