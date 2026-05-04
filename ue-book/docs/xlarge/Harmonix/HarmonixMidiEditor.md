# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、MIDI资产、MetaSound节点） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Epic Games 的 Harmonix GenTech 团队开发的**专业音乐音频处理插件包**，提供完整的音乐制作和交互式音频功能。该插件解决的核心问题是：在游戏引擎中实现**音乐感知的音频处理**，包括：

- **MIDI 文件处理**：导入、解析、编辑 MIDI 文件，支持标准 MIDI 格式
- **DSP 音频处理**：提供专业级数字信号处理算法，用于音乐相关的音频效果
- **MetaSound 集成**：将音乐功能集成到 UE5 的 MetaSound 节点图系统中，实现可视化音频编程
- **音乐同步**：支持音乐节拍同步、时间线控制等游戏音频常见需求

该插件特别适用于需要**音乐交互性**的游戏项目，如节奏游戏、音乐可视化、动态配乐系统等。

## 使用场景

- 你在开发**节奏游戏**（如 Guitar Hero 风格）→ 使用 HarmonixMidi 处理 MIDI 谱面数据
- 你需要实现**动态音乐系统**，根据游戏状态切换音乐层 → 使用 HarmonixDsp + HarmonixMetasound
- 你要创建**音乐可视化效果**，需要实时分析音频频谱 → 使用 HarmonixDsp 的 DSP 节点
- 你需要在 MetaSound 中添加**音乐理论功能**（和弦、音阶、调性）→ 使用 HarmonixMetasound 节点
- 你要导入和编辑**MIDI 文件**作为游戏资产 → 使用 HarmonixMidi + HarmonixMidiEditor

## 模块架构

```
Harmonix (插件根)
├── Harmonix                    ← 核心模块，基础功能
├── HarmonixDsp                 ← DSP 音频处理算法
├── HarmonixDspEditor           ← DSP 编辑器工具
├── HarmonixDspTests            ← DSP 单元测试
├── HarmonixEditor              ← 核心编辑器功能
├── HarmonixMetasound           ← MetaSound 节点集成
├── HarmonixMetasoundEditor     ← MetaSound 编辑器
├── HarmonixMetasoundTests      ← MetaSound 单元测试
├── HarmonixMidi                ← MIDI 文件处理
├── HarmonixMidiEditor          ← MIDI 编辑器（资产导入/右键菜单）
└── HarmonixMidiTests           ← MIDI 单元测试
```

### 模块说明

| 模块 | 类型 | 说明 |
|---|---|---|
| `Harmonix` | Runtime | 核心基础模块，提供公共类型定义和基础功能 |
| `HarmonixDsp` | Runtime | 数字信号处理算法，音频效果处理 |
| `HarmonixDspEditor` | Runtime | DSP 相关的编辑器扩展和工具 |
| `HarmonixDspTests` | Runtime | DSP 模块的自动化测试 |
| `HarmonixEditor` | Runtime | 核心编辑器功能扩展 |
| `HarmonixMetasound` | Runtime | MetaSound 节点图集成，提供音乐相关节点 |
| `HarmonixMetasoundEditor` | Runtime | MetaSound 集成的编辑器工具 |
| `HarmonixMetasoundTests` | Runtime | MetaSound 集成的自动化测试 |
| `HarmonixMidi` | Runtime | MIDI 文件解析和处理核心功能 |
| `HarmonixMidiEditor` | Runtime | MIDI 资产编辑器，支持导入和右键菜单操作 |
| `HarmonixMidiTests` | Runtime | MIDI 模块的自动化测试 |

## 子模块文档

由于 Harmonix 是一个大型插件（722 个源文件），各子模块有独立文档：

| 子模块 | 文档链接 | 说明 |
|---|---|---|
| HarmonixMidi | [HarmonixMidi.md](HarmonixMidi.md) | MIDI 文件处理核心 |
| HarmonixMidiEditor | [HarmonixMidiEditor.md](HarmonixMidiEditor.md) | MIDI 编辑器工具 |
| HarmonixDsp | [HarmonixDsp.md](HarmonixDsp.md) | DSP 音频处理 |
| HarmonixMetasound | [HarmonixMetasound.md](HarmonixMetasound.md) | MetaSound 集成 |

## 模块依赖

从各模块的 Build.cs 提取的独特依赖（排除标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册和发现，用于 MIDI/音频资产管理 |
| `UnrealEd` | 编辑器功能，用于资产工厂和导入导出 |
| `MetasoundEngine` | MetaSound 引擎集成（HarmonixMetasound 依赖） |
| `MetasoundFrontend` | MetaSound 前端节点图（HarmonixMetasound 依赖） |
| `Harmonix` | 核心模块，所有子模块的基础依赖 |
| `HarmonixMidi` | MIDI 处理核心（HarmonixMidiEditor 依赖） |
| `HarmonixDsp` | DSP 处理核心（HarmonixDspEditor 依赖） |

## 维护状态

### 近期更新

```
- 2024-xx-xx 9803c443cfab 为包含对应 .gen.cpp 的源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME（使用 UnrealCodeFixup 应用）
- 2024-xx-xx bbf3a553c72f [Harmonix] 如果 PreferredReimportPath 从未设置，则不发出警告。修复了 Content Browser 中重新导入选项不起作用的 bug
- 2024-xx-xx 6ad78437cac6 确保 MidiFileFactory 仅重新导入具有正确扩展名的文件
```

### 维护评价

**综合评价：实验性插件，活跃开发中**

- **创建时间**：2024 年 1 月，相对较新的插件
- **维护状态**：活跃维护中，近期有功能性更新和 bug 修复
- **实验性标记**：`IsExperimentalVersion: true`，表明仍在实验阶段
- **默认启用**：`EnabledByDefault: false`，需要手动启用
- **团队背景**：由 Epic Games 的 Harmonix GenTech 团队开发，Harmonix 是知名音乐游戏开发商（Guitar Hero、Rock Band），技术实力有保障

**注意事项**：
- ⚠️ 该插件标记为实验性，API 可能在未来版本中发生变化
- ⚠️ 需要手动在项目设置中启用
- ✅ 有完整的单元测试覆盖（DspTests、MetasoundTests、MidiTests）
- ✅ 由 Epic Games 官方团队维护，质量有保障

**推荐使用**：如果你的项目需要专业的音乐音频处理功能，特别是节奏游戏或动态音乐系统，推荐使用。但需注意实验性状态，做好 API 变化的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix)
- 官方文档：暂无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspTests)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests)

---

# HarmonixMidiEditor

> MIDI 文件编辑器模块，提供 MIDI 资产的导入、编辑和管理功能。

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HarmonixMidiEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiEditor) | |

## 用途

HarmonixMidiEditor 是 Harmonix 插件的 MIDI 编辑器模块，专门负责 **MIDI 文件资产的编辑器集成**。该模块解决的问题是：

- **MIDI 文件导入**：提供资产工厂（Asset Factory），支持将标准 MIDI 文件（.mid）导入为 UE 资产
- **资产右键菜单**：在 Content Browser 中为 MIDI 资产添加自定义右键菜单操作
- **重新导入支持**：支持 MIDI 文件的重新导入功能，保持资产引用不变
- **文件扩展名验证**：确保只导入正确扩展名的 MIDI 文件

该模块是 HarmonixMidi 核心模块的编辑器扩展，为开发者提供便捷的 MIDI 资产管理工作流。

## 使用场景

- 你有一个 **MIDI 谱面文件**，需要导入到 UE 项目中作为节奏游戏的数据源 → 使用 HarmonixMidiEditor 导入 .mid 文件
- 你需要**更新已导入的 MIDI 文件**，但不想破坏现有的蓝图引用 → 使用重新导入功能
- 你想在 Content Browser 中**快速访问 MIDI 相关操作** → 通过右键菜单执行
- 你开发了一个**自定义 MIDI 处理工具**，需要集成到编辑器 → 扩展 FMidiFileActions

## 蓝图用法

该模块主要提供编辑器扩展功能，不直接暴露蓝图节点。MIDI 资产的蓝图操作在 HarmonixMidi 核心模块中。

### 编辑器功能

| 功能 | 说明 | 触发方式 |
|---|---|---|
| 导入 MIDI 文件 | 将 .mid 文件导入为 UMidiFile 资产 | Content Browser → Import |
| 重新导入 | 更新已导入的 MIDI 资产 | Content Browser → 右键 → Reimport |
| 资产操作菜单 | MIDI 资产的自定义右键菜单 | Content Browser → 右键 MIDI 资产 |

## C++ 用法

### 头文件引入

```cpp
#include "HarmonixMidiEditorModule.h"
```

### 模块接口

HarmonixMidiEditor 模块提供标准的 IModuleInterface 实现：

```cpp
// Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiEditor/Public/HarmonixMidiEditorModule.h

class FHarmonixMidiEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    
private:
    // 注册 MIDI 资产的右键菜单
    void RegisterAssetContextMenus();
};
```

### 日志类别

```cpp
// 使用 HarmonixMidiEditor 日志类别
DECLARE_LOG_CATEGORY_EXTERN(LogHarmonixMidiEditor, Log, All);

// 在代码中使用
UE_LOG(LogHarmonixMidiEditor, Log, TEXT("MIDI file imported: %s"), *FileName);
```

### 资产操作类

```cpp
// FMidiFileActions 提供 MIDI 文件的编辑器操作
class FMidiFileActions
{
    // 具体实现细节在 .cpp 中
    // 主要功能：
    // - 文件导入验证
    // - 重新导入逻辑
    // - 右键菜单注册
};
```

## Demo 示例

### 自定义 MIDI 资产操作

```cpp
// MyMidiTools.h
#pragma once

#include "CoreMinimal.h"
#include "HarmonixMidi/Classes/MidiFile.h"

class FMyMidiTools
{
public:
    // 检查 MIDI 文件是否有效
    static bool ValidateMidiFile(const FString& FilePath)
    {
        // 检查文件扩展名
        if (!FilePath.EndsWith(TEXT(".mid"), ESearchCase::IgnoreCase))
        {
            UE_LOG(LogTemp, Warning, TEXT("Invalid MIDI file extension: %s"), *FilePath);
            return false;
        }
        
        // 检查文件是否存在
        if (!FPaths::FileExists(FilePath))
        {
            UE_LOG(LogTemp, Error, TEXT("MIDI file not found: %s"), *FilePath);
            return false;
        }
        
        return true;
    }
    
    // 获取 MIDI 文件信息
    static void LogMidiFileInfo(UMidiFile* MidiFile)
    {
        if (!MidiFile)
        {
            return;
        }
        
        UE_LOG(LogTemp, Log, TEXT("MIDI File Info:"));
        UE_LOG(LogTemp, Log, TEXT("  Track Count: %d"), MidiFile->GetNumTracks());
        UE_LOG(LogTemp, Log, TEXT("  Duration: %.2f seconds"), MidiFile->GetDurationSeconds());
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HarmonixMidi` | MIDI 核心处理模块，提供 UMidiFile 等基础类型 |
| `AssetRegistry` | 资产注册和发现，用于 MIDI 资产管理 |
| `UnrealEd` | 编辑器功能，用于资产工厂和导入导出 |

## 维护状态

### 近期更新

```
- 2024-xx-xx 9803c443cfab 为包含对应 .gen.cpp 的源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME（使用 UnrealCodeFixup 应用）
- 2024-xx-xx bbf3a553c72f [Harmonix] 如果 PreferredReimportPath 从未设置，则不发出警告。修复了 Content Browser 中重新导入选项不起作用的 bug
- 2024-xx-xx 6ad78437cac6 确保 MidiFileFactory 仅重新导入具有正确扩展名的文件
```

### 维护评价

**综合评价：实验性模块，活跃维护中**

- **创建时间**：2024 年 1 月，与 Harmonix 插件同时创建
- **维护状态**：活跃维护中，近期有重要的 bug 修复
- **实验性标记**：继承父插件的实验性状态
- **代码质量**：有标准的模块接口实现，日志类别定义完善

**近期修复的重要问题**：
- ✅ 修复了重新导入选项不起作用的 bug（PreferredReimportPath 警告问题）
- ✅ 确保只重新导入正确扩展名的文件，避免误操作
- ✅ 添加了 UE_INLINE_GENERATED_CPP_BY_NAME 优化编译性能

**推荐使用**：该模块是 HarmonixMidi 的必要编辑器扩展，如果你使用 HarmonixMidi 处理 MIDI 数据，该模块会自动启用。功能稳定，近期修复了重要的导入相关 bug。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiEditor)
- [HarmonixMidi 核心模块](HarmonixMidi.md)
- [Harmonix 插件主页](../index.md)