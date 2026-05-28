# Unreal Animation Framework (UAF)

> Framework for defining functional data flow for animation systems

| 属性 | 值 |
|---|---|
| 中文名 | 虚幻动画框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画框架资产） |
| 模块 | `UAF` (Runtime), `UAFEditor` (Runtime), `UAFTestData` (Runtime), `UAFUncookedOnly` (Runtime), `UAFTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF) | |

## 用途

UAF (Unreal Animation Framework) 是一个实验性的动画系统框架，旨在通过"功能数据流"的方式重新构建 UE 的动画系统架构。从源码分析来看，它主要解决以下问题：

1. **数据驱动的动画系统**：将动画逻辑从传统的行为树/状态机模式转向声明式的数据流模式，允许将动画变量（如速度、位置、朝向）直接绑定到游戏逻辑中
2. **类型安全的变量绑定**：通过 `FBindableXxx` 系列类型（如 `FBindableBool`, `FBindableFloat`, `FBindableVector`）实现类型安全的动画数据绑定，避免运行时类型错误
3. **子属性绑定**：支持绑定结构体的子属性（如 `FVector.X`, `FQuat.Rotator()`），提供更精细的动画控制
4. **性能优化**：通过批量解析和缓存机制，优化大量动画变量的绑定性能

UAF 不同于传统的动画蓝图系统，它更侧重于底层数据流的定义和优化，适合需要高性能、数据驱动动画的复杂项目。

## 使用场景

- 你需要构建一个高度数据驱动的动画系统，将游戏状态直接映射到动画参数 → 使用 UAF 的变量绑定系统
- 你的项目需要处理大量动画变量（如 100+ 个浮点数/向量），传统动画蓝图性能不足 → 使用 UAF 的批量解析和性能优化
- 你需要在运行时动态改变动画变量的来源（如从网络同步、物理模拟、AI 决策等） → 使用 UAF 的灵活绑定机制
- 你需要精确控制动画子属性（如骨骼旋转的单个分量） → 使用 UAF 的子属性绑定功能
- 你正在开发高性能的动画中间件或自定义动画系统 → 使用 UAF 作为底层框架

## 蓝图用法

UAF 当前为实验性插件，且主要用于底层框架开发，蓝图接口相对有限。主要功能集中在 C++ 层。

### 核心节点

从源码分析，UAF 的蓝图接口主要集中在动画蓝图和变量绑定方面，但由于其为实验性功能，具体蓝图节点需要在实际项目中启用后查看。

### 使用示例（蓝图描述）

由于 UAF 是底层框架，其蓝图使用通常与动画蓝图系统集成：

1. **创建动画蓝图**：在动画蓝图中创建基于 UAF 的动画图
2. **绑定游戏变量**：将游戏逻辑中的变量（如角色速度、跳跃状态）绑定到动画参数
3. **配置数据流**：定义变量之间的数据流向和转换逻辑
4. **运行时调整**：在游戏运行时动态调整绑定关系或数据源

## C++ 用法

### 头文件引入

```cpp
#include "UAFTestVars.h"  // 测试数据结构
#include "UAF/UAF.h"       // 核心框架
```

### 基本用法

UAF 主要通过结构体和变量绑定机制工作：

```cpp
// 包含 UAF 测试数据结构（来源：Engine/Plugins/Experimental/UAF/UAF/Source/UAFTestData/Public/UAFTestVars.h）
#include "UAFTestVars.h"

// 创建一个包含各种动画变量的测试结构体
FUAFTestVars TestVars;
TestVars.bBool = true;
TestVars.FloatVal = 3.14f;
TestVars.VectorVar = FVector(1.0f, 2.0f, 3.0f);

// 创建性能测试结构体
FUAFPerfVars10 PerfVars;
PerfVars.f0 = 1.0f;
PerfVars.v0 = FVector(10.0f, 20.0f, 30.0f);
```

### 进阶用法

UAF 的核心功能在于变量绑定系统：

```cpp
// 假设有 UAF 核心类（需要实际项目中使用）
// 创建可绑定的变量
FBindableFloat BoundFloat;
FBindableVector BoundVector;

// 绑定到游戏数据
BoundFloat.BindTo(GetCharacterSpeed());  // 绑定到角色速度
BoundVector.BindTo(GetCharacterLocation());  // 绑定到角色位置

// 子属性绑定示例
FBindableFloat BoundZComponent;
BoundZComponent.BindToSubProperty(GetCharacterLocation(), &FVector::Z);  // 只绑定 Z 分量

// 批量解析优化（用于大量变量的性能优化）
TArray<FBindableFloat> FloatBindings;
// ... 添加多个绑定

// 批量解析（UAF 内部优化机制）
// 解析所有绑定，准备动画系统使用
```

## Demo 示例

以下是一个最小的 UAF 使用示例，展示如何创建和使用测试数据结构：

```cpp
// UAFDemoCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "UAFTestVars.h"
#include "UAFDemoCharacter.generated.h"

UCLASS()
class AUAFDemoCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AUAFDemoCharacter();

    // UAF 测试变量
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UAF")
    FUAFTestVars AnimationVars;

    // 性能测试变量
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UAF|Performance")
    FUAFPerfVars10 PerformanceVars;

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
};

// UAFDemoCharacter.cpp
#include "UAFDemoCharacter.h"

AUAFDemoCharacter::AUAFDemoCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AUAFDemoCharacter::BeginPlay()
{
    Super::BeginPlay();
    
    // 初始化测试变量
    AnimationVars.bBool = true;
    AnimationVars.FloatVal = 0.0f;
    AnimationVars.VectorVar = FVector::ZeroVector;
    AnimationVars.QuatVar = FQuat::Identity;
    
    // 初始化性能测试变量
    for (int32 i = 0; i < 10; ++i)
    {
        PerformanceVars.f[i] = 0.0f;
        PerformanceVars.v[i] = FVector::ZeroVector;
    }
}

void AUAFDemoCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // 更新动画变量（模拟游戏逻辑）
    AnimationVars.FloatVal += DeltaTime;
    AnimationVars.VectorVar.X += DeltaTime * 100.0f;
    AnimationVars.QuatVar *= FQuat(FVector::UpVector, DeltaTime * 0.5f);
    
    // 更新性能测试变量
    for (int32 i = 0; i < 10; ++i)
    {
        PerformanceVars.f[i] = FMath::Sin(GetWorld()->GetTimeSeconds() + i * 0.1f);
        PerformanceVars.v[i] = FVector(PerformanceVars.f[i], 
                                      PerformanceVars.f[i] * 2.0f, 
                                      PerformanceVars.f[i] * 3.0f);
    }
    
    // 在实际项目中，这些变量会通过 UAF 绑定系统传递给动画系统
}
```

## 模块依赖

从 UAF 插件的模块结构分析，以下模块依赖需要注意：

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 支持实时代码编辑和热重载功能，用于开发调试 |

其他依赖为常见的 UE 核心模块（Core, CoreUObject, Engine 等）。

**注意**：UAF 是一个大型插件，包含多个模块。实际使用时，根据所需功能选择依赖对应的模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `eeaff753` | UAF: Introduce optional tick dependency between the UAF Component targeting a ACharacters mesh compo | 为 UAF 组件添加可选的 Tick 依赖，针对角色网格体组件优化更新顺序 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间可移植 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中使用的范围枚举可能导致垃圾输出的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式说明符在 32 位和 64 位参数间的不匹配问题 |
| 2026-04-24 | `523ac953` | Fix incorrect quaternion attribute type usage | 修复不正确的四元数属性类型使用 |

### 维护评价

**活跃维护中** ✅

UAF 是 Epic Games 的实验性动画框架，从 Git 记录来看：
1. **创建时间较新**：2025 年 6 月创建，距今约 1 年
2. **持续更新**：最近几个月有多个实质性更新，包括功能添加（Tick 依赖）、编译器兼容性修复和 bug 修复
3. **开发活跃**：由 Epic Games 工程师维护，与 UE 主开发分支同步更新
4. **实验性状态**：标记为实验性 (`IsExperimentalVersion: true`)，默认未启用，说明可能在未来有较大改动
5. **推荐使用**：适合对动画系统有深度定制需求的项目，但需要做好 API 变动的准备

**注意**：由于是实验性插件，生产环境使用需谨慎，建议仅在研发或实验项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF)
- [官方文档](https://docs.unrealengine.com) (暂无专门文档，需参考源码)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF/Tests)

## 子模块概览

UAF 插件包含以下模块，每个模块有不同的用途：

| 模块 | 类型 | 用途 |
|---|---|---|
| **UAF** | Runtime | 核心框架，包含动画数据流、变量绑定等基础功能 |
| **UAFEditor** | Runtime | 编辑器扩展，提供 UAF 的可视化编辑工具 |
| **UAFTestData** | Runtime | 测试数据结构，包含各种类型的测试变量和性能基准数据 |
| **UAFUncookedOnly** | Runtime | 仅未打包时使用的功能，用于开发调试 |
| **UAFTests** | Runtime | 自动化测试，包含单元测试和性能测试 |

## UAFTestData 模块详情

UAFTestData 模块主要用于提供测试数据结构，支持 UAF 系统的单元测试和性能基准测试。

### 核心数据结构

| 结构体 | 用途 | 包含属性类型 |
|---|---|---|
| `FUAFTestVars` | 基础测试变量 | bool, float, double, int32, FVector, FQuat, FTransform, 嵌套结构体 |
| `FUAFPerfVars10` | 性能测试变量 | 10个 float/bool/double/int32/int64/uint8/FName/枚举/FQuat/向量 |
| `FUAFNestedTestStruct` | 嵌套结构体测试 | FVector, FQuat, FTransform |
| `FUAFPackedByteStruct` | 紧凑内存布局测试 | 相邻的小字段（uint8, 枚举, float） |

### 使用场景

1. **单元测试**：验证 FBindableXxx 类型的绑定和解析功能
2. **性能基准**：测试大量变量绑定时的性能表现
3. **边界测试**：测试各种数据类型和嵌套结构体的处理
4. **内存布局测试**：测试紧挨着的小字段（如相邻的 uint8）是否会被错误读取