// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

contract MyEstate {
    enum EstateType{ House, Flat, Loft}
    enum AdStatus {Opened, Closed}

    struct Estate{
        uint size;
        string estateAddress;
        address owner;
        EstateType esType;
        bool isActive;
        uint idEstate;
    }
     
    struct Advertisement{
        address owner;
        address buyer;
        uint price;
        uint idEstate;
        uint dateTime;
        AdStatus adStatus;
    }

    Estate[] estates;
    Advertisement[] ads;

    mapping (address=>uint) balances;

    event estateCreated(address _owner, uint _idAstate, uint _dateTime, EstateType _esType);
    event adCreated(address _owner, uint _idEstate, uint _idAd, uint _dateTime, uint _price);
    event estateStatusChanged(address _owner, uint _idEstate, uint _dateTime, bool _isActive);
    event adStatusChanged(address _owner, uint _idEstate, uint idAd, uint _dateTime, AdStatus _adStatus);
    event fundsBack(address _to, uint _value, uint _dateTime);
    event estatePurchased(address _owner, address _buyer, uint _idAd, uint _idEstate, AdStatus _adStatus, uint _dateTime, uint _price);
    event Payd(address _from, uint _amount);

    modifier enoughValue (uint value, uint price){
        require(value >= price, unicode"У вас недостаточно средств");
        _;
    }

    modifier onlyEstateOwner (uint idEstate){
        require(estates[idEstate-1].owner == msg.sender, unicode"Вы не владелец данной недвижимости");
        _;
    }

    modifier onlyAddOwner (uint idAd){
        require(ads[idAd].owner == msg.sender, unicode"Вы не владелец данного объявления");
        _;
    }

    modifier isActiveEstate (uint idEstate){
        require(estates[idEstate-1].isActive, unicode"Данная недвижимость недоступна");
        _;
    }

    modifier isCloseAd (uint idAd){
        require(ads[idAd-1].adStatus == AdStatus.Opened, unicode"Данное объявление закрыто");
        _;
    }

    function createEstate(uint size, string memory estateAddress, EstateType esType) public{
        require(size > 1, unicode"Размер должен быт > 1");
        estates.push(Estate(size, estateAddress, msg.sender, esType, true, estates.length + 1));
        emit estateCreated(msg.sender, estates.length + 1, block.timestamp, esType);
    }

    function createAd(uint price, uint idEstate, AdStatus adStatus) onlyEstateOwner(idEstate) isActiveEstate(idEstate) public{
        ads.push(Advertisement(msg.sender, address(0), price, idEstate, block.timestamp, adStatus));
        emit adCreated(msg.sender, idEstate, ads.length + 1, block.timestamp, price);
    }
    
    function changeStatusEstate(uint idEstate) onlyEstateOwner(idEstate) public{
        estates[idEstate-1].isActive = false;
        emit estateStatusChanged(msg.sender, idEstate, block.timestamp, false);

        for (uint i = 0; i < ads.length; i++){
            if (ads[i].idEstate == idEstate){
                ads[i].adStatus = AdStatus.Closed;
                emit adStatusChanged(msg.sender, idEstate, i+1, block.timestamp, AdStatus.Closed);
            }
        }
    }

    function changeStatusAd(uint idAd, uint idEstate) public onlyAddOwner(idAd-1) isActiveEstate(idEstate){
        ads[idAd-1].adStatus = AdStatus.Closed; 
        emit adStatusChanged(msg.sender, idEstate, idAd, block.timestamp, AdStatus.Closed);
    }

    function withDraw(uint value) public{
        require(value > balances[msg.sender], unicode"У вас недостаточно средств на смарт контракте");
        require(value < 0, unicode"Значение для вывода должно быть больше 0");
        payable(msg.sender).transfer(value);
        balances[msg.sender] -= value;
        emit fundsBack(msg.sender, value, block.timestamp);
    }

    function buyEstate(uint idAd) public isCloseAd(idAd) enoughValue(balances[msg.sender], ads[idAd-1].price){
        ads[idAd-1].adStatus = AdStatus.Closed;
        estates[ads[idAd-1].idEstate-1].isActive = false;
        balances[ads[idAd-1].owner] += ads[idAd-1].price;
        balances[msg.sender] -= ads[idAd-1].price;
        emit estatePurchased(ads[idAd-1].owner, msg.sender, idAd, ads[idAd-1].idEstate, ads[idAd-1].adStatus, block.timestamp, ads[idAd-1].price);
    }

    function getBalance() public  view returns(uint) {
        return balances[msg.sender];
    }

    function getEstates() public view returns(Estate[] memory){
        return estates;
    }

    function getAds() public view returns(Advertisement[] memory){
        return ads;
    }

    function pay() public payable {
        balances[msg.sender] += msg.value;
        emit Payd(msg.sender, msg.value);
    }
}