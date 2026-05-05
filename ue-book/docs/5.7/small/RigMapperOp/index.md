# RigMapper Op

> Experimental Retarget Op for re-mapping curves using RigMapper Definitions

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | false (Installed: false) |
| 包含内容 | true |
| 模块 | RigMapperOp (Runtime) |
| 创建时间 | 2025-09-09 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/RigMapperOp) | |

## 用途

RigMapperOp 是一个 **IK Retargeter Op（重定向操作）**，用于在动画重定向过程中对动画曲线进行重映射。

核心功能：将 RigMapperOp 嵌入到 IK Retargeter 的 Op Stack 中，利用 [RigMapper](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/RigMapper) 插件的 `URigMapperDefinition` 资产来定义输入曲线到输出曲线的映射关系。在运行时或导出动画时，自动将源骨骼的曲线按定义映射到目标骨骼。

该插件解决的问题是：当两个骨架使用不同的曲线命名约定或曲线值含义时，需要在重定向阶段做一次曲线翻译。RigMapperOp 让这个过程可以完全配置化（通过 RigMapper Definition 资产），而不需要编写自定义代码。

## 使用场景

- 你在使用 IK Retargeter 做动画重定向，源和目标骨架的面部表情曲线命名不一致 → 添加 RigMapper Op 并指定 RigMapperDefinition 来做曲线映射
- 源和目标是同一骨架但 RigMapper 只覆盖部分控制曲线 → 开启 `bCopyAllSourceCurves` 让未映射的曲线直接透传
- 你有一套标准化的面部曲线定义，需要在不同 MetaHuman / 自定义角色间迁移 → 用 RigMapperOp 做桥接

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSettings` | 获取当前 RigMapper Op 的设置（返回 `FIKRetargetRigMapperOpSettings`） | `UIKRetargetRigMapperOpController` |
| `SetSettings` | 设置 RigMapper Op 的设置（传入 `FIKRetargetRigMapperOpSettings`） | `UIKRetargetRigMapperOpController` |

### 设置结构体: FIKRetargetRigMapperOpSettings

| 属性 | 类型 | 说明 |
|---|---|---|
| `bCopyAllSourceCurves` | `bool` (默认 false) | 是否将所有源曲线复制到目标。true = 所有源曲线直接复制，RigMapper 只覆盖有映射的曲线；false = 只输出被映射的曲线 |
| `Definitions` | `TArray<URigMapperDefinition*>` | RigMapper 定义资产列表。按顺序执行，可用于链式映射 |

### 使用示例（蓝图描述）

1. 创建一个 `IK Retargeter` 资产
2. 在 Op Stack 中添加 **RigMapper** Op
3. 在 Details 面板中：
   - 将 `RigMapperDefinition` 资产拖入 `Definitions` 数组
   - 根据需要设置 `bCopyAllSourceCurves`（同骨架设 true，跨骨架设 false）
4. 通过 Blueprint 调用 `GetSettings` / `SetSettings` 可以运行时动态修改

## C++ 用法

### 头文件引入

```cpp
#include "RigMapperOp.h"
```

### 关键类

- **`FIKRetargetRigMapperOpSettings`** — 设置结构体，持有 `bCopyAllSourceCurves` 和 `Definitions` 数组
- **`FIKRetargetRigMapperOp`** — Op 实现，继承自 `FIKRetargetOpBase`，负责曲线的运行时映射和动画序列导出时的曲线处理
- **`UIKRetargetRigMapperOpController`** — 蓝图/Python API 控制器，提供 `GetSettings()` / `SetSettings()`

### 运行时处理流程

Op 在动画图中的执行分为两步：

1. **`AnimGraphPreUpdateMainThread`**（游戏线程）— 从源 `UAnimInstance` 获取当前 AttributeCurve，检查 Definition 是否变更并按需重新初始化
2. **`AnimGraphEvaluateAnyThread`**（任意线程）— 执行曲线映射：读取输入曲线 → 调用 `FRigMapperProcessor::EvaluateFrame` → 写入输出曲线

### 动画序列导出

`ProcessAnimSequenceCurves` 在批量导出动画时被调用，对整个动画序列的所有帧执行曲线重映射。如果 `bCopyAllSourceCurves=true`，未被映射的输入曲线会直接透传到输出。

### 定义优先级

如果目标 SkeletalMesh 上挂载了 `URigMapperDefinitionUserData`（Asset User Data），其 Definition 会覆盖 Op 设置中的 Definition。否则使用 Op 自身的 Definition 列表。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `AnimationCore` | 动画核心数据结构 |
| `IKRig` | IK Retargeter 框架（提供 `FIKRetargetOpBase` 基类） |
| `RigMapper` | RigMapper 处理器和 Definition 资产 |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `IKRig` | IK Retargeter Op Stack 框架 |
| `RigMapper` | `URigMapperDefinition`、`FRigMapperProcessor` 等核心类 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-09 | `2024999` | [RigMapper] second part of moving RigMapper Op into separate plugin | RigMapperOp 从 RigMapper 插件中独立为单独的 Experimental 插件 |

仅有一次 commit，表明这是从 RigMapper 主插件中拆分出来的独立模块。

### 维护评价

- **创建时间**: 2025-09-09（不到 1 年前）
- **状态**: 🆕 新建实验性插件
- **维护活跃度**: 该插件只有一次初始拆分 commit，但 RigMapper / IKRetargeter 相关代码（由 kiaran.ritchie 维护）在 2025 年 9 月有密集更新，说明上游模块仍在活跃开发
- **是否推荐使用**: 可以使用，但需注意 `IsExperimentalVersion: true`，API 可能在后续版本中变化
- **限制**: 标记为 Experimental，未在 Installed 中声明为默认可用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/RigMapperOp)
- [RigMapper 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/RigMapper)（核心依赖）
- [IKRig 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/IKRig)（Retargeter 框架）
