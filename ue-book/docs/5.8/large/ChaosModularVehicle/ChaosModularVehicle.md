# Chaos Modular Vehicle

> Modular Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 模块化载具 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-14 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle) | |

## 用途

ChaosModularVehicle 是基于 Chaos 物理引擎构建的**模块化载具仿真框架**。它将传统的一体式载具组件拆分为独立的仿真模块（引擎、传动、悬挂、车轮等），每个模块可单独配置和组合。

核心思路是利用 Geometry Collection（几何体集合）作为底层数据结构来管理载具各部件的变换和仿真索引（`FModularSimCollection`），让不同物理仿真模块能够共享统一的空间变换树，同时又各自拥有独立的仿真逻辑。

**为什么存在？** 传统 UE 载具系统（WheeledVehicle）采用单一刚体 + 约束的黑盒方式，难以灵活组合和扩展。ChaosModularVehicle 通过模块化架构解决了以下问题：
- 载具各子系统（引擎、变速箱、悬挂、车轮）可以独立替换和配置
- 基于 Chaos 物理引擎的高性能仿真
- 网络同步下的载具物理状态一致性
- 简化骨骼网格体方案下的兼容性

## 使用场景

- 你需要在赛车游戏中实现高度可定制的载具物理（不同引擎/悬挂组合） → 用 ChaosModularVehicle
- 你需要将载具物理分解为独立模块，由不同设计师分别调参 → 用 ChaosModularVehicle
- 你需要在多人游戏中正确同步载具物理状态 → ChaosModularVehicle 已内置网络物理支持
- 你需要比传统 WheeledVehicle 更灵活的载具仿真架构 → 用 ChaosModularVehicle

## 模块架构

```
ChaosModularVehicle (插件)
├── ChaosModularVehicle      [Runtime]  核心数据结构与仿真集合
│   └── FModularSimCollection — 基于 GeometryCollection 的模块化仿真数据
├── ChaosModularVehicleEngine [Runtime]  载具仿真引擎逻辑
│   └── 引擎扭矩、传动比、车轮力计算等
└── ChaosModularVehicleEditor [UncookedOnly]  编辑器工具
    └── 载具配置编辑器、调试可视化
```

## 蓝图用法

> **注意**：此插件为实验性功能，蓝图 API 可能在后续版本中变动。

### 核心节点

基于源码分析，以下为与载具交互的主要蓝图接口：

| 节点 | 说明 | 所在模块 |
|---|---|---|
| 载具输入控制 | 通过 EnhancedInput 驱动载具油门/转向/刹车 | `ChaosModularVehicleEngine` |
| 调试扭矩显示 | 修复后正确报告引擎扭矩数值 | `ChaosModularVehicleEditor` |
| 网络控制判断 | 基于 NetworkPhysicsComponent 判断本地控制 | `ChaosModularVehicleEngine` |

### 使用示例（蓝图描述）

1. **创建载具 Pawn**：在 Pawn 蓝图中添加模块化载具组件，配置各仿真模块（引擎、传动、悬挂、车轮）
2. **绑定输入**：使用 EnhancedInput Action 绑定油门（Throttle）、转向（Steering）、刹车（Brake）输入
3. **网络同步**：载具物理状态自动通过 NetworkPhysicsComponent 进行网络同步

## C++ 用法

### 头文件引入

```cpp
#include "ChaosModularVehicle/ModularSimCollection.h"
#include "ChaosModularVehicle/ChaosModularVehiclePlugin.h"
```

### 基本用法：创建模块化仿真集合

```cpp
// 来源: Public/ChaosModularVehicle/ModularSimCollection.h

// 创建空的模块化仿真集合
Chaos::FModularSimCollection* SimCollection = Chaos::FModularSimCollection::NewModularSimulationCollection();

// 或从已有的 TransformCollection 创建
Chaos::FModularSimCollection* SimCollection = Chaos::FModularSimCollection::NewModularSimulationCollection(BaseTransforms);

// 初始化集合（分配必要属性）
Chaos::FModularSimCollection::Init(SimCollection);
```

### 进阶用法：访问仿真模块索引

```cpp
// 来源: Public/ChaosModularVehicle/ModularSimCollection.h

// FModularSimCollection 内部维护了每个变换节点对应的仿真模块索引
// SimModuleIndex 属性将 TransformGroup 中的每个节点映射到对应的仿真模块

// 获取仿真模块索引属性名称
const FName SimModuleIndexAttr = Chaos::FModularSimCollection::SimModuleIndexAttribute;

// 通过 TManagedArray 访问某个节点的仿真模块索引
int32 ModuleIdx = SimCollection->SimModuleIndex[TransformNodeIndex];

// 生成仿真树结构
SimCollection->GenerateSimTree();
```

### 模块接口访问

```cpp
// 来源: Public/ChaosModularVehicle/ChaosModularVehiclePlugin.h

// 检查模块是否可用
if (IChaosModularVehiclePlugin::IsAvailable())
{
    // 获取模块接口
    IChaosModularVehiclePlugin& PluginModule = IChaosModularVehiclePlugin::Get();
}
```

## Demo 示例

### 模块化载具基础用法

```cpp
// MyModularVehicle.h
#pragma once

#include "GameFramework/Pawn.h"
#include "ChaosModularVehicle/ModularSimCollection.h"
#include "MyModularVehicle.generated.h"

UCLASS()
class AMyModularVehicle : public APawn
{
    GENERATED_BODY()

public:
    AMyModularVehicle();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    // 模块化仿真集合（由 Chaos 物理系统管理）
    TUniquePtr<Chaos::FModularSimCollection> SimCollection;
};
```

```cpp
// MyModularVehicle.cpp
#include "MyModularVehicle.h"
#include "ChaosModularVehicle/ChaosModularVehiclePlugin.h"

AMyModularVehicle::AMyModularVehicle()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyModularVehicle::BeginPlay()
{
    Super::BeginPlay();

    // 确保模块已加载
    if (IChaosModularVehiclePlugin::IsAvailable())
    {
        // 创建模块化仿真集合
        SimCollection.Reset(Chaos::FModularSimCollection::NewModularSimulationCollection());
        if (SimCollection.IsValid())
        {
            Chaos::FModularSimCollection::Init(SimCollection.Get());
            SimCollection->GenerateSimTree();
        }
    }
}

void AMyModularVehicle::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 载具物理由 Chaos 物理线程驱动，此处处理游戏逻辑
}
```

## 模块依赖

### ChaosModularVehicle 模块

| 模块 | 用途 |
|---|---|
| `GeometryCollectionEngine` | FModularSimCollection 的基类 FGeometryCollection 来源 |
| `Chaos` | Chaos 物理引擎核心 |

### ChaosModularVehicleEngine 模块

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 载具输入系统（插件级依赖） |
| `NetworkPhysics` | 网络物理同步支持 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `EnhancedInput` | 载具操控输入 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `cd96428a` | ChaosModularVehicle: Fix ShowDebug engine torque always reporting 0 | 修复调试显示中引擎扭矩始终为 0 的问题 |
| 2026-04-23 | `be90176f` | Modular Vehicle: Fix the vehicle setup for the simplified skeletal mesh case when running networked. | 修复简化骨骼网格体在网络模式下的载具初始化 |
| 2026-04-16 | `4ea9aba8` | [NetPhysics] Fix IsLocallyControlled ensure on physics thread in ModularVehicle | 修复物理线程上 IsLocallyControlled 的断言错误 |
| 2026-04-14 | `bd0ef478` | [ModularVehicle] Rely on NetworkPhysicsComponent.IsLocallyControlled from the Modular Vehicle instead | 统一使用 NetworkPhysicsComponent 的 IsLocallyControlled 判断 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF 新接口 |

### 维护评价

**活跃维护中** 🟢

- **年龄**：约 2.7 年，属于较新的插件
- **更新频率**：最近 1 个月内有多次实质性提交，维护频率高
- **更新内容**：涵盖网络同步修复、调试工具改进、代码现代化（日志宏迁移），表明插件正在积极打磨中
- **实验性状态**：`IsExperimentalVersion=true`，`Installed=false`，需手动启用
- **网络支持**：近期大量 commit 涉及网络物理同步，表明网络化载具是重点开发方向

**注意事项**：
- 此为实验性插件，API 可能在后续版本中发生重大变化
- 依赖 Chaos 物理引擎和 EnhancedInput，确保这些系统可用
- 版本号 0.1，表明仍处于早期开发阶段

**推荐**：✅ 适合对载具物理有深度定制需求且愿意承担实验性 API 变动风险的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle)
- [ModularSimCollection 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/ChaosModularVehicle/Source/ChaosModularVehicle/Public/ChaosModularVehicle/ModularSimCollection.h)
- [ChaosModularVehiclePlugin 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/ChaosModularVehicle/Source/ChaosModularVehicle/Public/ChaosModularVehicle/ChaosModularVehiclePlugin.h)