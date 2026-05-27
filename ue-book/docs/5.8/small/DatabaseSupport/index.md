# Database Support

> Abstract Database Support

| 属性 | 值 |
|---|---|
| 中文名 | 数据库支持 |
| 分类 | Database |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatabaseSupport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/DatabaseSupport) | |

## 用途

该插件提供了一套**抽象的数据库访问接口**，其本身不实现任何具体的数据库连接功能，而是定义了用于数据库查询和结果集处理的基础类。它的存在是为了在UE项目中提供一个统一的数据库访问抽象层，使得其他插件（例如 SQLiteSupport）可以在其基础上实现具体的数据库连接和操作。

这个插件解决的核心问题是：为不同平台（特别是不支持直接数据库连接的平台）提供一个标准化的、可扩展的数据库访问框架，使得游戏或应用能够以一致的方式与各种数据库进行交互。

## 使用场景

- 你需要为你的UE项目集成数据库功能，但又不想直接依赖某个特定的数据库（如MySQL、SQLite）时，可以基于此抽象层开发。
- 你正在为一个不支持直接数据库连接的平台（如某些主机平台）开发，需要一个能在所有平台上运行的数据库访问方案。
- 你正在开发一个需要数据持久化功能的游戏或应用（例如存档系统、配置管理），并希望以标准化的方式处理数据库操作。

## 蓝图用法

此插件**不包含任何蓝图可调用的函数或属性**。它是一个纯 C++ 运行时模块，旨在被其他模块（插件）引用和扩展，而非直接在蓝图中使用。

## C++ 用法

该插件主要定义了三个核心类，用于抽象数据库连接和结果集。

### 头文件引入

```cpp
#include "DatabaseSupport/Database.h"
```

### 基本用法

**1. 使用 `FDataBaseConnection` 连接数据库并执行命令**

```cpp
// 假设我们有一个具体的数据库连接类（例如来自SQLiteSupport插件）
FDataBaseConnection* MyConnection = CreateDatabaseConnection(); // 此函数需由具体实现提供

// 打开连接
const TCHAR* ConnectionString = TEXT("MyDatabase.db");
bool bSuccess = MyConnection->Open(ConnectionString, nullptr, nullptr);

if (bSuccess)
{
    // 执行非查询命令（如 CREATE TABLE）
    MyConnection->Execute(TEXT("CREATE TABLE IF NOT EXISTS PlayerData (ID INTEGER PRIMARY KEY, Name TEXT)"));
    
    // 执行查询命令
    FDataBaseRecordSet* RecordSet = nullptr;
    if (MyConnection->Execute(TEXT("SELECT * FROM PlayerData"), RecordSet))
    {
        // 处理结果集
        if (RecordSet && !RecordSet->HasError())
        {
            // ... 见下方示例
        }
        // 重要：调用者负责删除返回的 RecordSet
        delete RecordSet;
    }
    
    // 关闭连接
    MyConnection->Close();
}

// 重要：调用者负责删除连接对象
delete MyConnection;
```

**2. 遍历 `FDataBaseRecordSet` 结果集**

```cpp
// 假设 RecordSet 是从查询中获得的有效指针
FDataBaseRecordSet* RecordSet = ...; 

// 方法一：使用内置的 TIterator
for (FDataBaseRecordSet::TIterator It(RecordSet); It; ++It)
{
    // It 指向当前的 RecordSet
    FString PlayerName = It->GetString(TEXT("Name"));
    int32 PlayerId = It->GetInt(TEXT("ID"));
    UE_LOG(LogTemp, Log, TEXT("Player %d: %s"), PlayerId, *PlayerName);
}

// 方法二：手动遍历
RecordSet->MoveToFirst(); // 虽然TIterator会自动调用，但手动调用也可以
while (!RecordSet->IsAtEnd())
{
    FString Value = RecordSet->GetString(TEXT("SomeColumn"));
    // ... 处理数据
    RecordSet->MoveToNext();
}
```

**3. 获取结果集的列信息**

```cpp
TArray<FDatabaseColumnInfo> Columns = RecordSet->GetColumnNames();
for (const FDatabaseColumnInfo& ColInfo : Columns)
{
    FString TypeName;
    switch (ColInfo.DataType)
    {
    case DBT_FLOAT: TypeName = TEXT("Float"); break;
    case DBT_INT: TypeName = TEXT("Int"); break;
    case DBT_STRING: TypeName = TEXT("String"); break;
    default: TypeName = TEXT("Unknown"); break;
    }
    UE_LOG(LogTemp, Log, TEXT("Column: %s (Type: %s)"), *ColInfo.ColumnName, *TypeName);
}
```

## Demo 示例

这是一个展示如何继承并实现抽象接口的最小示例。

**MyDatabaseConnection.h**
```cpp
#pragma once
#include "DatabaseSupport/Database.h"

class FMyDatabaseConnection : public FDataBaseConnection
{
public:
    virtual bool Open(const TCHAR* ConnectionString, const TCHAR* RemoteConnectionIP, const TCHAR* RemoteConnectionStringOverride) override;
    virtual void Close() override;
    virtual bool Execute(const TCHAR* CommandString) override;
    virtual bool Execute(const TCHAR* CommandString, FDataBaseRecordSet*& RecordSet) override;

private:
    // 假设的内部状态
    bool bIsOpen = false;
};
```

**MyDatabaseConnection.cpp**
```cpp
#include "MyDatabaseConnection.h"

bool FMyDatabaseConnection::Open(const TCHAR* ConnectionString, const TCHAR* RemoteConnectionIP, const TCHAR* RemoteConnectionStringOverride)
{
    // 实现具体的数据库连接逻辑
    bIsOpen = true;
    UE_LOG(LogTemp, Log, TEXT("Database opened: %s"), ConnectionString);
    return bIsOpen;
}

void FMyDatabaseConnection::Close()
{
    // 实现具体的关闭逻辑
    bIsOpen = false;
}

bool FMyDatabaseConnection::Execute(const TCHAR* CommandString)
{
    if (!bIsOpen) return false;
    UE_LOG(LogTemp, Log, TEXT("Executing command: %s"), CommandString);
    // 实现具体的命令执行
    return true;
}

bool FMyDatabaseConnection::Execute(const TCHAR* CommandString, FDataBaseRecordSet*& RecordSet)
{
    if (!bIsOpen || !Execute(CommandString))
    {
        RecordSet = nullptr;
        return false;
    }
    // 实现具体的查询并返回 RecordSet
    // RecordSet = new FMyDatabaseRecordSet(...);
    return true;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。由于这是一个提供抽象接口的基础模块，它本身不依赖其他特定的功能模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-31 | `c8c0f285` | PR #12093: add error detection for SQLiteSupport | 为SQLiteSupport插件增加了错误检测功能 |
| 2025-06-13 | `185bf170` | Replace some usages of FORCEINLINE with inline in Engine modules. | 将部分FORCEINLINE用法替换为inline，进行代码风格统一 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了内置插件的供应商链接以使用安全协议（HTTPS） |
| 2019-12-27 | `360d078c` | Second batch of remaining Engine copyright updates. | 进行了第二批引擎版权信息更新 |

### 维护评价

**维护不活跃**。该插件创建于2019年，是一个非常基础的抽象层。最近的更新（2025年10月）是针对依赖此插件的`SQLiteSupport`进行的功能性改动，而非对`DatabaseSupport`本身的核心逻辑更新。之前的更新大多是代码风格或元数据的批量修改，非实质性功能更新。该插件作为基础设施，功能稳定，但长期缺乏针对其本身的功能演进。

由于它是隐藏的（Hidden: true）且默认不启用（EnabledByDefault: false），主要被其他插件依赖，普通用户通常不会直接使用。如果你的项目需要基础的数据库抽象层，可以依赖它，但需注意它本身不提供任何具体的数据库连接实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/DatabaseSupport)
- [官方文档](无)