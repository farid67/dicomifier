#ifndef _f86951f5_4869_47a1_bd24_f082f3f1e8f1
#define _f86951f5_4869_47a1_bd24_f082f3f1e8f1

#include "Condition.h"

namespace router
{

namespace conditions
{

/**
 * @brief Condition that is always false.
 */
class False: public Condition
{
public:
    typedef False Self;
    typedef std::shared_ptr<Self> Pointer;
    typedef std::shared_ptr<Self const> ConstPointer;

    static Pointer New() { return Pointer(new Self()); }
    ~False();

    virtual bool eval() const;
    
    static std::string get_class_name() { return "False"; }

protected:
    False();

private:
    False(Self const & other); // Purposely not implemented
    Self const & operator=(Self const & other); // Purposely not implemented
};

} // namespace conditions

} // namespace router

#endif // _f86951f5_4869_47a1_bd24_f082f3f1e8f1
