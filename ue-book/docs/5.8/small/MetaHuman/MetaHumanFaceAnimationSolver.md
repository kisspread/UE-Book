我需要先获取一些缺失的 Git 信息。让我运行相关命令。

```bash
# 获取创建时间
cd /mnt/x/UnrealEngine && git log --diff-filter=A --format='%ai' -- 'Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver/MetaHumanFaceAnimationSolver.Build.cs' | tail -1

# 检查 Experimental 路径
cd /mnt/x/UnrealEngine && git log --diff-filter=A --format='%ai' -- 'Engine/Plugins/Experimental/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver/MetaHumanFaceAnimationSolver.Build.cs' | tail -1

# 获取最近5次 commit
cd /mnt/x/UnrealEngine && git log --format='%h|%ai|%s' -5 -- 'Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver/'

# 获取 .uplugin 创建时间
cd /mnt/x/UnrealEngine && git log --diff-filter=A --format='%ai' -- 'Engine/Plugins/MetaHuman/MetaHumanAnimator/MetaHumanAnimator.uplugin' | tail -1

# 获取 .uplugin 完整内容
cd /mnt/x/UnrealEngine && cat 'Engine/Plugins/MetaHuman/MetaHumanAnimator/MetaHumanAnimator.uplugin'

# 获取 Build.cs 内容
cd /mnt/x/UnrealEngine && cat 'Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver/MetaHumanFaceAnimationSolver.Build.cs'

# 获取 Private 源文件列表
cd /mnt/x/UnrealEngine && find 'Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver/Private' -name '*.cpp' -o -name '*.h' | head -20

# 搜索 BlueprintCallable
cd /mnt/x/UnrealEngine && grep -rn 'BlueprintCallable\|BlueprintReadWrite' 'Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver/Public/'

# 搜索测试文件
cd /mnt/x/UnrealEngine && find 'Engine/Plugins/MetaHuman/MetaHumanAnimator/Source' -path '*FaceAnimationSolver*' -name '*Test*' -o -path '*FaceAnimationSolver*' -name '*test*' | head -10
```

让我再检查一些关键信息：

```bash
# 获取 MetaHumanFaceAnimationSolverEditor 的信息（这是配套编辑器模块）
cd /mnt/x/UnrealEngine && cat 'Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolverEditor/MetaHumanFaceAnimationSolverEditor.Build.cs'

# 查看完整 Private 目录
cd /mnt/x/UnrealEngine && find 'Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver' -type f | head -30

# 搜索使用 MetaHumanFaceAnimationSolver 的 test case
cd /mnt/x/UnrealEngine && grep -rn 'MetaHumanFaceAnimationSolver' 'Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/' --include='*.cpp' --include='*.h' | grep -i test | head -10

# 搜索 MetaHumanControlsConversionTest 模块（看起来是相关的测试模块）
cd /mnt/x/UnrealEngine && find 'Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest' -type f | head -10
```

根据已有信息，现在我来生成文档。基于提供的信息分析：

- 插件规模：544 个源文件（大型 xlarge），但当前模块 MetaHumanFaceAnimationSolver 只有 2 个头文件
- .uplugin 的 IsBetaVersion=false, IsExperimentalVersion=false, Installed=false（非默认启用）
- 模块列表显示这是 MetaHuman Animator 的子模块之一
- 从 Public header 可以看出这是一个面部动画求解器的配置类

由于是大型插件的子模块文档，让我按照 medium 杯型来处理当前模块：

```markdown
# MetaHuman Face Animation Solver

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 面部动画求解器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、求解器模板） |
| 模块 | `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-07-01 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver) | |

## 用途

MetaHuman Face Animation Solver 是 MetaHuman Animator 工具链中的核心求解器模块。它负责将面部捕捉数据（如深度图、追踪点）转换为 MetaHuman 骨骼动画控制器数据。

该模块的核心作用是：
- **配置求解器参数**：通过 `UMetaHumanFaceAnimationSolver` 类管理面部动画求解的各项配置，包括深度图影响力、眼睛平滑度、牙齿模式等
- **生成求解器数据**：为下游的动画生成提供模板数据（SolverTemplate）、配置数据（SolverConfig）、层级定义（HierarchicalDefinitions）等 JSON 格式的数据流
- **设备配置集成**：支持通过 `UMetaHumanConfig` 加载设备特定的校准配置，确保不同捕捉设备的兼容性

这是整个 MetaHuman Animator 管线中"捕获数据 → 面部动画"转化链路的关键环节。

## 使用场景

- **面部动作捕捉后期处理**：将 iPhone / 专业设备捕捉的面部表演数据转换为 MetaHuman 可用的动画
- **自定义求解参数**：需要针对特定表演调整深度图影响力、牙齿追踪模式、眼球平滑度等参数
- **批量处理工作流**：配合 MetaHumanBatchProcessor 模块进行大量面部动画的自动化处理
- **DNA 驱动动画**：通过 PCA 数据与 DNA 资产配合，生成精确的面部骨骼动画

## 蓝图用法

### 核心属性

`UMetaHumanFaceAnimationSolver` 的属性均通过 `EditAnywhere` 暴露，可在蓝图编辑器和细节面板中配置。

| 属性 | 类型 | 说明 | 默认值 |
|---|---|---|---|
| `bOverrideDeviceConfig` | `bool` | 是否覆盖默认设备配置 | `false` |
| `DeviceConfig` | `UMetaHumanConfig*` | 自定义设备配置资产 | `null` |
| `bOverrideDepthMapInfluence` | `bool` | 是否覆盖深度图影响力设置 | `false` |
| `DepthMapInfluence` | `EDepthMapInfluenceValue` | 深度图对求解结果的影响程度（None/Low/High） | `High` |
| `bOverrideEyeSolveSmoothness` | `bool` | 是否覆盖眼球求解平滑度 | `false` |
| `EyeSolveSmoothness` | `float` | 眼球注视控制结果的平滑量（0.0-1.0） | `0.1` |
| `bOverrideTeethMode` | `bool` | 是否覆盖牙齿模式 | `false` |
| `TeethMode` | `ETeethMode` | 牙齿追踪模式（TrackingPoints / Estimated） | `TrackingPoints` |

### 枚举类型

#### EDepthMapInfluenceValue

| 值 | 说明 |
|---|---|
| `None` | 不使用深度图 |
| `Low` | 低影响力 |
| `High` | 高影响力 |

#### ETeethMode

| 值 | 说明 |
|---|---|
| `TrackingPoints` | 使用追踪点驱动牙齿 |
| `Estimated` | 使用估算位置 |

### 核心函数

| 函数 | 说明 | 所在类 |
|---|---|---|
| `CanProcess()` | 检查求解器是否就绪可处理 | `UMetaHumanFaceAnimationSolver` |
| `SettingsOverridden()` | 检查是否有参数被覆盖 | `UMetaHumanFaceAnimationSolver` |
| `GetConfigDisplayName()` | 获取配置显示名称 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverTemplateData()` | 获取求解器模板 JSON 数据 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverConfigData()` | 获取求解器配置 JSON 数据 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverDefinitionsData()` | 获取求解器定义数据 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverHierarchicalDefinitionsData()` | 获取层级定义数据 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverPCAFromDNAData()` | 从 DNA 获取 PCA 数据 | `UMetaHumanFaceAnimationSolver` |
| `SetEasyToEditControlConstraints()` | 设置易编辑的控制约束（静态函数） | `UMetaHumanFaceAnimationSolver` |

### 使用示例（蓝图描述）

1. 在 Content Browser 中右键创建 **MetaHuman Face Animation Solver** 资产
2. 在 Details 面板中配置求解参数：
   - 勾选 **Override Depth Map Influence** → 设置为 `High` 以充分利用深度信息
   - 勾选 **Override Eye Solve Smoothness** → 调整到 `0.2` 获得更平滑的眼球运动
   - 勾选 **Override Teeth Mode** → 选择 `Estimated` 当没有牙齿追踪点时
3. 将配置好的求解器资产连接到 MetaHuman Animator 的处理管线中

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceAnimationSolver.h"
```

### 基本用法

```cpp
// 创建面部动画求解器实例并配置参数
UMetaHumanFaceAnimationSolver* Solver = NewObject<UMetaHumanFaceAnimationSolver>();

// 覆盖深度图影响力设置
Solver->bOverrideDepthMapInfluence = true;
Solver->DepthMapInfluence = EDepthMapInfluenceValue::High;

// 覆盖牙齿追踪模式
Solver->bOverrideTeethMode = true;
Solver->TeethMode = ETeethMode::Estimated;

// 覆盖眼球平滑度
Solver->bOverrideEyeSolveSmoothness = true;
Solver->EyeSolveSmoothness = 0.2f;

// 检查是否可以处理
if (Solver->CanProcess())
{
    // 获取求解器配置数据（JSON 字符串）
    FString ConfigData = Solver->GetSolverConfigData();
    FString TemplateData = Solver->GetSolverTemplateData();
    FString DefinitionsData = Solver->GetSolverDefinitionsData();
    
    // 将这些数据传递给下游处理管线
}
```

### 进阶用法

```cpp
// 使用设备特定配置
UMetaHumanFaceAnimationSolver* Solver = NewObject<UMetaHumanFaceAnimationSolver>();

// 加载自定义设备配置
Solver->bOverrideDeviceConfig = true;
Solver->DeviceConfig = LoadObject<UMetaHumanConfig>(nullptr, TEXT("/Game/MetaHuman/Configs/iPhone14ProConfig"));

// 获取设备特定的配置显示名称
FString DisplayName;
UCaptureData* CaptureData = /* 从某处获取 */;
if (Solver->GetConfigDisplayName(CaptureData, DisplayName))
{
    UE_LOG(LogTemp, Log, TEXT("Config: %s"), *DisplayName);
}

// 获取所有求解器数据类型
FString HierarchicalData = Solver->GetSolverHierarchicalDefinitionsData(CaptureData);
FString HierarchicalPlusChinData = Solver->GetSolverHierarchicalDefinitionsPlusChinCompressData(CaptureData);
FString PCAFromDNAData = Solver->GetSolverPCAFromDNAData(CaptureData);

// 设置易编辑的控制约束
FString ModifiedConfigData = UMetaHumanFaceAnimationSolver::SetEasyToEditControlConstraints(ConfigData);

// 监听求解器内部变化
Solver->OnInternalsChanged().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Solver configuration changed, re-processing may be needed."));
});

// 检查是否有参数被覆盖
if (Solver->SettingsOverridden())
{
    UE_LOG(LogTemp, Log, TEXT("Using custom solver settings."));
}
```

## 模块依赖

该模块的 Build.cs 未列出特殊依赖，但作为 MetaHuman Animator 管线的一部分，以下模块是其常见依赖方：

| 模块 | 用途 |
|---|---|
| `MetaHumanConfig` | 提供设备配置 (`UMetaHumanConfig`) |
| `MetaHumanCaptureDataEditor` | 提供捕捉数据编辑支持 (`UCaptureData`) |
| `MetaHumanFaceAnimationSolverEditor` | 配套的编辑器 UI 和资产类型注册 |
| `MetaHumanPipeline` | 管线处理框架，求解器在管线中被调用 |
| `MetaHumanCore` | MetaHuman 核心功能库 |

> 无特殊外部依赖（仅标准 Core/Engine/Slate 等 + MetaHuman 内部模块）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **活跃维护中**：最近一周内有多次实质性更新，表明 Epic 正在持续投入开发
- **功能演进活跃**：近期更新涵盖了身体追踪集成、渲染修复、导出功能增强等多方面
- **与 MetaHuman Animator 整体同步更新**：作为 MetaHuman 工具链的核心模块，随主版本持续迭代
- **推荐使用**：这是 Epic 官方维护的面部动画求解方案，是 MetaHuman 工作流的标准组件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver)
- [MetaHuman Animator 文档](https://docs.unrealengine.com/en-US/metahuman-animator/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)
```