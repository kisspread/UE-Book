# MetaSound

> A high-performance audio system that enables sound designers to have complete control over audio DSP graph generation of sound sources, via sample-accurate control and modulation of sound using audio parameters and audio events from game data and Blueprints

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（标准音频节点库） |
| 模块 | `MetasoundEditor` (Runtime), `MetasoundEngine` (Runtime), `MetasoundEngineTest` (Runtime), `MetasoundFrontend` (Runtime), `MetasoundGenerator` (Runtime), `MetasoundGraphCore` (Runtime), `MetasoundStandardNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-22 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound) | |

---

## 用途

MetaSound 是 UE5 的下一代音频系统，用**节点图（DSP Graph）**取代传统 Sound Cue 的线性播放逻辑。它解决的核心问题是：**让声音设计师在采样级别（sample-accurate）完全掌控音频信号的生成、处理和调制流程**。

与传统 Sound Cue 相比，MetaSound 的关键差异：

- **程序化音频**：音频信号由节点图实时计算生成，而非简单播放预制波形
- **采样精确控制**：参数变化精确到音频采样级别，无延迟、无插值误差
- **蓝图深度集成**：游戏数据（如速度、距离、生命值）可通过 Audio Parameter 直接驱动音频图
- **运行时动态修改**：支持在播放过程中动态修改图结构（Dynamic Graph Transform）
- **操作符缓存池**：通过 `FOperatorPool` 复用已构建的操作符实例，减少运行时开销
- **实例计数与性能追踪**：内置并发实例计数器和 CSV 性能分析支持

MetaSound 本质上是一个**音频领域的可视化编程环境**，类似于材质编辑器之于着色器。

## 使用场景

- 你在制作开放世界游戏，需要风声随海拔和风速实时变化 → 用 MetaSound 构建参数化环境音
- 你需要武器音效根据射击距离、弹药类型动态混合 → 用 MetaSound + Audio Parameter 驱动
- 你要实现音乐系统的自适应过渡（如战斗 ↔ 探索） → 用 MetaSound 的触发器和状态机节点
- 你需要精确的音频同步（如节拍同步的视觉效果） → MetaSound 的 sample-accurate 时序
- 你在做音频原型或实验性 DSP 效果 → MetaSound 节点图快速迭代

## 子模块概览

本插件规模为 **xlarge**（648 源文件），按功能拆分为 7 个模块：

| 模块 | 类型 | 职责 |
|---|---|---|
| **MetasoundGraphCore** | Runtime | 图核心抽象层：节点、顶点、边、操作符接口定义 |
| **MetasoundFrontend** | Runtime | 前端层：图的序列化、注册表、资产管理、蓝图接口 |
| **MetasoundGenerator** | Runtime | 运行时生成器：操作符构建、缓存池、音频缓冲区输出 |
| **MetasoundEngine** | Runtime | 引擎集成层：与 USoundBase/FAudioDevice 的桥接 |
| **MetasoundStandardNodes** | Runtime | 标准节点库：数学、滤波器、振荡器、包络等内置节点 |
| **MetasoundEditor** | Runtime | 编辑器：MetaSound 编辑器 UI、图表编辑、节点面板 |
| **MetasoundEngineTest** | Runtime | 自动化测试用例 |

> 各子模块的详细文档请参阅对应的子页面。

## 蓝图用法

MetaSound 的蓝图交互主要通过 **Audio Parameter** 和 **MetaSound Source** 资产实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Float Parameter` | 设置 MetaSound 实例的浮点参数 | `UAudioComponent` |
| `Set Int Parameter` | 设置整数参数 | `UAudioComponent` |
| `Set Bool Parameter` | 设置布尔参数 | `UAudioComponent` |
| `Set String Parameter` | 设置字符串参数 | `UAudioComponent` |
| `Set Trigger Parameter` | 触发一个事件（如播放、停止） | `UAudioComponent` |
| `Play Sound` / `Spawn Sound` | 播放/生成 MetaSound 源 | `UGameplayStatics` |

### 使用示例（蓝图描述）

**示例 1：根据玩家速度驱动脚步声频率**

1. 创建一个 MetaSound Source 资产，在图中添加一个 `Float` 输入参数命名为 `Speed`
2. 将 `Speed` 连接到一个乘法节点，再连接到触发器的频率控制
3. 在蓝图中：
   - `Event Tick` → `Get Velocity` → `Vector Length` → `Set Float Parameter`（Target: Audio Component, In Name: "Speed"）

**示例 2：通过 Trigger 参数控制音效生命周期**

1. MetaSound 图中添加 `Trigger` 类型输入 `OnHit`
2. `OnHit` 连接到一个包络发生器（ADSR），再连接到输出
3. 蓝图中：`On Component Hit` → `Set Trigger Parameter`（In Name: "OnHit"）

## C++ 用法

### 头文件引入

```cpp
// 操作符缓存池与生成器
#include "MetasoundGenerator.h"
#include "MetasoundOperatorCache.h"

// 实例计数
#include "MetasoundInstanceCounter.h"

// 模块接口
#include "MetasoundGeneratorModule.h"
```

### 基本用法：获取操作符池和实例计数器

```cpp
// 来源: MetasoundGeneratorModule.h
// 通过模块接口获取全局操作符池和实例计数管理器

#include "MetasoundGeneratorModule.h"

void SetupMetaSoundServices()
{
    IMetasoundGeneratorModule& GeneratorModule = 
        FModuleManager::GetModuleChecked<IMetasoundGeneratorModule>("MetasoundGenerator");
    
    // 获取操作符池（用于缓存和复用已构建的操作符）
    TSharedPtr<Metasound::FOperatorPool> OperatorPool = 
        GeneratorModule.GetOperatorPool();
    
    // 获取实例计数管理器（用于追踪运行中的 MetaSound 实例数）
    TSharedPtr<Metasound::FConcurrentInstanceCounterManager> CounterManager = 
        GeneratorModule.GetOperatorInstanceCounterManager();
}
```

### 基本用法：实例计数追踪

```cpp
// 来源: MetasoundInstanceCounter.h
// 使用 RAII 方式追踪 MetaSound 实例的生命周期

#include "MetasoundInstanceCounter.h"

class FMyAudioController
{
    TSharedPtr<Metasound::FConcurrentInstanceCounterManager> CounterManager;
    TUniquePtr<Metasound::FConcurrentInstanceCounter> InstanceCounter;

public:
    void StartMetaSound(const FTopLevelAssetPath& AssetPath)
    {
        // RAII 计数器：构造时自动 Increment，析构时自动 Decrement
        InstanceCounter = MakeUnique<Metasound::FConcurrentInstanceCounter>(
            AssetPath, CounterManager
        );
    }

    void QueryStats()
    {
        // 查询某个资产的当前实例数
        int64 CurrentCount = CounterManager->GetCountForPath(AssetPath);
        
        // 查询历史峰值
        int64 PeakCount = CounterManager->GetPeakCountForPath(AssetPath);
        
        // 遍历所有资产的统计信息
        CounterManager->VisitStats([](const FTopLevelAssetPath& Path, int64 Count)
        {
            UE_LOG(LogTemp, Log, TEXT("Asset: %s, Active Instances: %lld"), 
                *Path.ToString(), Count);
        });
    }
};
```

### 进阶用法：操作符池与预构建

```cpp
// 来源: MetasoundOperatorCache.h
// 使用 FOperatorBuildData 预构建操作符并缓存到池中

#include "MetasoundOperatorCache.h"

void PreBuildOperators()
{
    // 构建数据：指定初始化参数、注册表键、资产 ID 和实例数
    Metasound::FOperatorBuildData BuildData(
        MoveTemp(InitParams),          // FGeneratorInitParams
        RegistryKey,                    // Frontend::FGraphRegistryKey
        AssetClassID,                   // FGuid
        3,                              // 预构建 3 个实例
        true                            // bTouchExisting: 复用已有实例
    );
    
    // 操作符池设置
    Metasound::FOperatorPoolSettings PoolSettings;
    PoolSettings.MaxNumOperators = 128;  // 最大缓存操作符数
    
    // 通过 FOperatorPool 提交构建请求
    // 操作符会在后台线程异步构建并缓存
}
```

## Demo 示例

以下展示如何创建一个简单的 MetaSound 实例计数管理器：

### MyMetaSoundManager.h

```cpp
#pragma once

#include "MetasoundInstanceCounter.h"
#include "MetasoundGeneratorModule.h"
#include "UObject/TopLevelAssetPath.h"

class FMyMetaSoundManager
{
public:
    void Initialize();
    void Shutdown();

    // 播放一个 MetaSound 并追踪其实例
    void PlayMetaSound(const FTopLevelAssetPath& AssetPath);
    
    // 停止追踪（释放计数器时自动递减）
    void StopMetaSound();
    
    // 打印当前所有活跃实例统计
    void PrintInstanceStats() const;

private:
    TSharedPtr<Metasound::FConcurrentInstanceCounterManager> CounterManager;
    TMap<FTopLevelAssetPath, TUniquePtr<Metasound::FConcurrentInstanceCounter>> ActiveInstances;
};
```

### MyMetaSoundManager.cpp

```cpp
#include "MyMetaSoundManager.h"

void FMyMetaSoundManager::Initialize()
{
    IMetasoundGeneratorModule& Module = 
        FModuleManager::GetModuleChecked<IMetasoundGeneratorModule>("MetasoundGenerator");
    
    CounterManager = Module.GetOperatorInstanceCounterManager();
}

void FMyMetaSoundManager::Shutdown()
{
    // RAII: 所有 FConcurrentInstanceCounter 析构时自动 Decrement
    ActiveInstances.Empty();
    CounterManager.Reset();
}

void FMyMetaSoundManager::PlayMetaSound(const FTopLevelAssetPath& AssetPath)
{
    if (!CounterManager.IsValid())
    {
        return;
    }

    // 创建 RAII 计数器（构造时 Increment）
    auto Counter = MakeUnique<Metasound::FConcurrentInstanceCounter>(
        AssetPath, CounterManager
    );
    
    ActiveInstances.Add(AssetPath, MoveTemp(Counter));
    
    UE_LOG(LogTemp, Log, TEXT("Started MetaSound: %s"), *AssetPath.ToString());
}

void FMyMetaSoundManager::StopMetaSound()
{
    // 移除最后一个实例（析构时自动 Decrement）
    if (ActiveInstances.Num() > 0)
    {
        auto It = ActiveInstances.CreateIterator();
        FTopLevelAssetPath Path = It.Key();
        ActiveInstances.Remove(Path);
        
        UE_LOG(LogTemp, Log, TEXT("Stopped MetaSound: %s"), *Path.ToString());
    }
}

void FMyMetaSoundManager::PrintInstanceStats() const
{
    if (!CounterManager.IsValid())
    {
        return;
    }

    CounterManager->VisitStats(
        [](const FTopLevelAssetPath& Path, int64 Count)
        {
            UE_LOG(LogTemp, Log, TEXT("  %s: %lld active instances"), 
                *Path.ToString(), Count);
        }
    );
}
```

## 模块依赖

从各模块 Build.cs 分析，MetaSound 的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | 前端图定义、序列化、注册表 |
| `MetasoundGraphCore` | 图核心抽象（节点、顶点、操作符接口） |
| `MetasoundGenerator` | 运行时生成器与操作符缓存池 |
| `MetasoundStandardNodes` | 内置标准音频处理节点 |
| `SignalProcessing` | 底层 DSP 信号处理库 |
| `AudioMixer` | 音频混音器集成 |
| `AudioPlatformSettings` | 平台音频配置 |

> 使用者通常只需依赖 `MetasoundEngine`（它会传递依赖上述模块）和 `MetasoundFrontend`（用于蓝图/编辑器交互）。

## 维护状态

### 近期更新

```
- 6695acb7b92d UE: Quick fix for compile error on consoles
- 3dcb934ebf78 Fix for unresolved namespace when building certain platforms #rb trivial #rnx
- c849c401a3a4 Part 1 of cutting down FName table bloat & string passing, copying, & parsing by moving implementation to use AssetPath wherever possible - Misc clean-up and removal of old code
```

### 维护评价

**活跃维护** ✅

MetaSound 是 Epic Games 重点投入的音频系统，从 UE5.0 起作为默认音频方案替代 Sound Cue。近期更新集中在：

- **性能优化**：FName 表膨胀问题修复，迁移到 AssetPath 以减少字符串拷贝
- **跨平台兼容**：持续修复主机平台编译问题
- **代码质量**：清理旧代码，改善命名空间管理

作为 UE5 音频管线的核心组件，MetaSound 持续获得 Epic 的工程投入。推荐所有新项目使用 MetaSound 替代 Sound Cue。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/overview-of-metasounds-in-unreal-engine/)