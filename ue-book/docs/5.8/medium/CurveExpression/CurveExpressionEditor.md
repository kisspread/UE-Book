# Curve Expression

> Experimental Curve Remapper using Simple Math Expressions

| 属性 | 值 |
|---|---|
| 中文名 | 曲线表达式 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CurveExpression` (Runtime), `CurveExpressionEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/CurveExpression) | |

## 用途

该插件提供了一套**动画权重曲线运行时重映射系统**，允许开发者通过简单的数学表达式对动画曲线值进行转换和重映射。

核心解决的问题：在动画系统中，动画曲线（如 Morph Target 权重、自定义曲线）的原始值经常不能直接使用，需要经过数学变换（缩放、偏移、钳制、混合等）。传统做法需要在蓝图中逐个处理，而 CurveExpression 允许你用一行数学表达式（如 `v * 0.5 + 0.3`、`remap(v, 0, 1, -1, 1)`）批量定义映射规则，并在运行时高效执行。

插件支持两种工作模式：
- **单骨骼映射**（RemapCurves）：对当前角色自身的动画曲线进行重映射
- **跨网格映射**（RemapCurvesFromMesh）：从另一个骨骼网格组件读取曲线并重映射，适用于复制姿势后需要自定义曲线处理的场景（如将身体的曲线映射到面部）

## 使用场景

- 你在做面部动画系统，Morph Target 的权重值范围需要从 `0-1` 映射到 `-1~1` → 用 CurveExpression 定义 `remap(v, 0, 1, -1, 1)`
- 你的角色有 Copy Pose 动画图，需要对复制过来的曲线做条件性处理 → 用 RemapCurvesFromMesh 节点
- 你需要用表达式驱动多个 Morph Target 的联动（如张嘴时自动调节脸颊权重）→ 为不同曲线定义不同的表达式
- 你想把曲线映射规则保存为数据资产，在多个动画蓝图中复用 → 用 CurveExpressionsDataAsset

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Curve Expression Map` | 纯函数节点，创建曲线名到表达式字符串的映射 | `UK2Node_MakeCurveExpressionMap` |
| `Remap Curves` | 动画图节点，在 AnimGraph 中对当前骨骼的曲线进行表达式重映射 | `UAnimGraphNode_RemapCurves` |
| `Remap Curves From Mesh` | 动画图节点，从另一个网格组件读取曲线并重映射 | `UAnimGraphNode_RemapCurvesFromMesh` |

### 使用示例（蓝图描述）

**在动画蓝图 AnimGraph 中使用：**

1. 打开动画蓝图，在 AnimGraph 中右键搜索 **"Remap Curves"**
2. 添加 `Remap Curves` 节点
3. 在节点的 Details 面板中找到 **Expressions** 属性
4. 在表达式编辑器中为每条曲线定义映射规则，格式为：
   - `CurveName: expression`，例如：`MouthOpen: v * 0.8`
   - 支持的运算：`+` `-` `*` `/` `()`、内置函数 `remap(v, min_in, max_in, min_out, max_out)`
5. 将该节点串联在动画姿势流水线中

**从其他网格复制并重映射：**

1. 在 AnimGraph 中添加 `Remap Curves From Mesh` 节点
2. 设置 **Source Mesh Component**（通常绑定到另一个骨骼网格组件变量）
3. 定义表达式规则，同上

**使用数据资产：**

1. 在内容浏览器中右键 → Animation → **Curve Expression Data Asset**
2. 在数据资产中编辑表达式列表
3. 在动画图节点的 Details 中引用该数据资产

## C++ 用法

### 头文件引入

```cpp
// 运行时模块（动画节点）
#include "AnimNode_RemapCurves.h"

// 编辑器模块（动画图节点）
#include "AnimGraphNode_RemapCurves.h"
#include "AnimGraphNode_RemapCurvesFromMesh.h"
```

### 基本用法

CurveExpression 的核心运行时逻辑封装在 `FAnimNode_RemapCurves` 和 `FAnimNode_RemapCurvesFromMesh` 中。表达式通过 `FCurveExpressionList` 结构体存储。

```cpp
// 在自定义动画节点中使用表达式列表
#include "AnimNode_RemapCurves.h"

// FCurveExpressionList 包含一组 "CurveName: Expression" 映射
// 例如: {"MouthOpen": "v * 0.5", "EyeBlink": "remap(v, 0, 1, -1, 1)"}
```

### 进阶用法

编辑器模块提供了 `IRemapCurvesDebuggingProvider` 接口，允许动画图节点在编辑器中进行表达式验证：

```cpp
// 自定义动画图节点可实现此接口以支持调试验证
#include "IRemapCurvesDebuggingProvider.h"

class UMyAnimGraphNode : public UAnimGraphNode_Base, public IRemapCurvesDebuggingProvider
{
    GENERATED_BODY()

public:
    // 判断当前是否有调试实例可供验证
    bool CanVerifyExpressions() const override;

    // 触发表达式验证（检查表达式语法是否正确、曲线名是否存在等）
    void VerifyExpressions() override;
};
```

## 模块依赖

从模块类型和头文件内容推断：

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 动画核心类型（曲线、骨骼引用等） |
| `AnimGraph` | 动画图编辑器基础设施 |
| `BlueprintGraph` | K2 蓝图节点支持 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏，属于代码规范化 |
| 2025-11-19 | `0dcd49ea` | Curve Expression: Add a remap(v, min_in, max_in, min_out, max_out) function. | 新增 remap() 内置函数，支持范围重映射 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加内联生成宏，优化编译性能 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 同上，编译优化 |
| 2025-05-31 | `52e3dac1` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 修正 DLL 导出标记位置，修复链接问题 |

### 维护评价

- **创建时间**：2022 年 3 月，约 3 年历史
- **实验性状态**：仍标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`，始终未毕业为正式插件
- **更新频率**：2025 年有多次更新，包括实质性的功能增强（新增 `remap()` 函数）和代码维护，表明仍在活跃维护
- **已知限制**：
  - 实验性插件，API 可能在未来版本中发生 breaking change
  - `EnabledByDefault=false`，需要手动在项目设置中启用
  - 表达式语法相对简单，复杂逻辑可能需要多节点组合
- **推荐程度**：⭐⭐⭐ 如果你需要在运行时对动画曲线做数学变换，这是最方便的方案。但由于是实验性插件，建议做好未来迁移的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/CurveExpression)
- [官方文档]()（暂无）
- [测试用例]()（未发现独立测试用例）